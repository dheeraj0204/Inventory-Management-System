"""Web application entry point and REST API for Inventory Management System."""

import os
import secrets
from typing import Any, Dict
from flask import Flask, jsonify, render_template, request, session
from app.config import ALLOWED_CATEGORIES, APP_TITLE, QUALITY_GOAL, STOCK_ADJUSTMENT_REASONS, VERSION
from app.database import initialize_database
from app.models.user import User
from app.services import audit_service, auth_service, inventory_service, product_service, tqm_service
from app.utils.logger import logger
from app.utils.validators import ValidationError


def create_app() -> Flask:
    """Creates and configures the Flask application."""
    # Ensure database tables and initial seed data exist
    initialize_database()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

    # Disable strict slashes so /api/products and /api/products/ both work
    app.url_map.strict_slashes = False

    # -------------------------------------------------------------------------
    # Helper to retrieve current session user
    # -------------------------------------------------------------------------
    def get_session_user() -> Dict[str, Any]:
        user_data = session.get("user")
        if not user_data:
            return {
                "id": 1,
                "username": "admin",
                "full_name": "System Administrator",
                "role": "Admin",
                "email": "admin@inventory.local",
            }
        return user_data

    # -------------------------------------------------------------------------
    # Frontend Page Route
    # -------------------------------------------------------------------------
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            app_title=APP_TITLE,
            version=VERSION,
            quality_goal=QUALITY_GOAL,
            allowed_categories=ALLOWED_CATEGORIES,
            adjustment_reasons=STOCK_ADJUSTMENT_REASONS,
        )

    # -------------------------------------------------------------------------
    # Auth Endpoints
    # -------------------------------------------------------------------------
    @app.route("/api/auth/me", methods=["GET"])
    def auth_me():
        user = get_session_user()
        return jsonify({"success": True, "user": user})

    @app.route("/api/auth/login", methods=["POST"])
    def auth_login():
        payload = request.get_json(silent=True) or {}
        username = payload.get("username", "").strip()
        password = payload.get("password", "")

        success, message, user = auth_service.authenticate(username, password)
        if not success or not user:
            return jsonify({"success": False, "message": message}), 401

        user_dict = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "email": user.email,
        }
        session["user"] = user_dict
        return jsonify({"success": True, "message": message, "user": user_dict})

    @app.route("/api/auth/register", methods=["POST"])
    def auth_register():
        payload = request.get_json(silent=True) or {}
        username = payload.get("username", "").strip()
        password = payload.get("password", "")
        full_name = payload.get("full_name", "").strip()
        email = payload.get("email", "").strip() or None
        role = payload.get("role", "Staff").strip()

        success, message, user = auth_service.register_user(
            username=username,
            password=password,
            full_name=full_name,
            email=email,
            role=role,
        )
        if not success or not user:
            return jsonify({"success": False, "message": message}), 400

        user_dict = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "email": user.email,
        }
        session["user"] = user_dict
        return jsonify({"success": True, "message": message, "user": user_dict})

    @app.route("/api/auth/logout", methods=["POST"])
    def auth_logout():
        session.pop("user", None)
        return jsonify({"success": True, "message": "Logged out successfully."})

    @app.route("/api/auth/demo-users", methods=["GET"])
    def auth_demo_users():
        return jsonify({
            "success": True,
            "users": [
                {
                    "role": "Admin",
                    "username": "admin",
                    "password": "admin123",
                    "desc": "Full Master Control, CRUD, Stock Adjustment, TQM Analytics",
                },
                {
                    "role": "Manager",
                    "username": "manager",
                    "password": "manager123",
                    "desc": "Catalog Operations, Stock Adjustments, Quality Audits",
                },
                {
                    "role": "Staff",
                    "username": "staff",
                    "password": "staff123",
                    "desc": "Catalog Viewing, Stock Movement Inspection",
                },
            ],
        })

    # -------------------------------------------------------------------------
    # Product Catalog Endpoints
    # -------------------------------------------------------------------------
    @app.route("/api/products", methods=["GET"])
    def list_products():
        category = request.args.get("category", "").strip() or "All"
        search_query = request.args.get("search", "").strip()
        low_stock = request.args.get("low_stock", "").lower() in ("true", "1", "yes")

        products = product_service.get_all_products(
            search_query=search_query,
            category_filter=category,
        )

        if low_stock:
            products = [p for p in products if p.is_low_stock]

        return jsonify({
            "success": True,
            "count": len(products),
            "products": [p.to_dict() for p in products],
        })

    @app.route("/api/products/<product_id>", methods=["GET"])
    def get_product(product_id: str):
        product = product_service.get_product_by_id(product_id)
        if not product:
            return jsonify({"success": False, "message": f"Product '{product_id}' not found."}), 404

        movements = inventory_service.get_stock_movements(product_id=product_id, limit=20)
        return jsonify({
            "success": True,
            "product": product.to_dict(),
            "movements": movements,
        })

    @app.route("/api/products/next-id", methods=["GET"])
    def next_product_id():
        next_id = product_service.generate_next_product_id()
        return jsonify({"success": True, "next_id": next_id})

    @app.route("/api/products", methods=["POST"])
    def create_product():
        data = request.get_json(silent=True) or {}
        reason = data.pop("change_reason", "New product registration via Web Portal")
        try:
            new_prod = product_service.create_product(data, change_reason=reason)
            return jsonify({
                "success": True,
                "message": f"Product '{new_prod.name}' registered successfully.",
                "product": new_prod.to_dict(),
            }), 201
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e), "field": e.field}), 400
        except Exception as e:
            logger.error(f"Error creating product: {e}", exc_info=True)
            return jsonify({"success": False, "message": str(e)}), 500

    @app.route("/api/products/<product_id>", methods=["PUT"])
    def update_product(product_id: str):
        data = request.get_json(silent=True) or {}
        reason = data.pop("change_reason", "Product master update via Web Portal")
        try:
            # If quantity is not supplied in update payload, preserve existing quantity
            if "quantity" not in data or data["quantity"] is None:
                existing = product_service.get_product_by_id(product_id)
                if existing:
                    data["quantity"] = existing.quantity

            updated_prod = product_service.update_product(product_id, data, change_reason=reason)
            return jsonify({
                "success": True,
                "message": f"Product '{updated_prod.product_id}' updated successfully.",
                "product": updated_prod.to_dict(),
            })
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e), "field": e.field}), 400
        except Exception as e:
            logger.error(f"Error updating product: {e}", exc_info=True)
            return jsonify({"success": False, "message": str(e)}), 500

    @app.route("/api/products/<product_id>", methods=["DELETE"])
    def delete_product(product_id: str):
        payload = request.get_json(silent=True) or {}
        reason = payload.get("reason", "Product decommissioned via Web Portal")
        try:
            deleted = product_service.delete_product(product_id, reason=reason)
            if not deleted:
                return jsonify({"success": False, "message": f"Product '{product_id}' not found."}), 404
            return jsonify({"success": True, "message": f"Product '{product_id}' deleted."})
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e), "field": e.field}), 400
        except Exception as e:
            logger.error(f"Error deleting product: {e}", exc_info=True)
            return jsonify({"success": False, "message": str(e)}), 500

    # -------------------------------------------------------------------------
    # Inventory & Stock Adjustment Endpoints
    # -------------------------------------------------------------------------
    @app.route("/api/inventory/adjust", methods=["POST"])
    def adjust_stock():
        payload = request.get_json(silent=True) or {}
        product_id = payload.get("product_id", "").strip()
        new_quantity = payload.get("new_quantity")
        reason = payload.get("reason", "").strip()

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required."}), 400
        if new_quantity is None:
            return jsonify({"success": False, "message": "New quantity is required."}), 400
        if not reason:
            return jsonify({"success": False, "message": "Adjustment reason is mandatory for audit trail."}), 400

        try:
            movement = inventory_service.adjust_stock(
                product_id=product_id,
                new_quantity=int(new_quantity),
                reason=reason,
            )
            # Fetch updated product to return current state
            prod = product_service.get_product_by_id(product_id)
            return jsonify({
                "success": True,
                "message": f"Stock adjusted for {product_id} ({movement.movement_type} {abs(movement.quantity_change)} units).",
                "movement": movement.to_dict(),
                "product": prod.to_dict() if prod else None,
            })
        except ValidationError as e:
            return jsonify({"success": False, "message": str(e), "field": e.field}), 400
        except Exception as e:
            logger.error(f"Error adjusting stock: {e}", exc_info=True)
            return jsonify({"success": False, "message": str(e)}), 500

    @app.route("/api/inventory/summary", methods=["GET"])
    def inventory_summary():
        summary = inventory_service.get_inventory_summary()
        products = product_service.get_all_products()
        low_stock_items = [p.to_dict() for p in products if p.is_low_stock]

        return jsonify({
            "success": True,
            "total_valuation": summary["total_valuation"],
            "total_units": summary["total_units"],
            "total_items": summary["total_products"],
            "low_stock_count": summary["low_stock_count"],
            "low_stock_items": low_stock_items,
            "category_breakdown": summary["category_breakdown"],
        })

    @app.route("/api/inventory/movements", methods=["GET"])
    def list_movements():
        product_id = request.args.get("product_id", "").strip() or None
        limit = int(request.args.get("limit", 100))
        movements = inventory_service.get_stock_movements(product_id=product_id, limit=limit)
        return jsonify({
            "success": True,
            "count": len(movements),
            "movements": movements,
        })

    # -------------------------------------------------------------------------
    # Audit Logs Endpoints
    # -------------------------------------------------------------------------
    @app.route("/api/audit/logs", methods=["GET"])
    def list_audit_logs():
        search_query = request.args.get("search", "").strip()
        action_filter = request.args.get("action", "All").strip()
        entity_id = request.args.get("entity_id", "").strip() or None
        limit = int(request.args.get("limit", 150))

        logs = audit_service.get_audit_logs(
            search_query=search_query,
            action_filter=action_filter,
            entity_id=entity_id,
            limit=limit,
        )
        return jsonify({
            "success": True,
            "count": len(logs),
            "logs": [l.to_dict() for l in logs],
        })

    # -------------------------------------------------------------------------
    # TQM Quality Analytics Endpoints
    # -------------------------------------------------------------------------
    @app.route("/api/tqm/summary", methods=["GET"])
    def tqm_summary():
        ctq_metrics = tqm_service.calculate_ctq_metrics()
        pareto_data = tqm_service.calculate_pareto_data()
        return jsonify({
            "success": True,
            "ctq_metrics": ctq_metrics,
            "pareto": pareto_data,
        })

    @app.route("/api/tqm/defects", methods=["GET", "POST"])
    def tqm_defects():
        if request.method == "POST":
            payload = request.get_json(silent=True) or {}
            category = payload.get("category", "").strip()
            description = payload.get("description", "").strip()
            severity = payload.get("severity", "Medium").strip()
            count = int(payload.get("occurrence_count", 1))
            action = payload.get("corrective_action", "").strip()
            try:
                defect = tqm_service.add_defect(
                    category=category,
                    description=description,
                    severity=severity,
                    occurrence_count=count,
                    corrective_action=action,
                )
                return jsonify({"success": True, "defect": defect.to_dict()}), 201
            except ValidationError as e:
                return jsonify({"success": False, "message": str(e), "field": e.field}), 400

        status_filter = request.args.get("status", "All").strip()
        defects = tqm_service.get_all_defects(status_filter=status_filter)
        return jsonify({"success": True, "defects": [d.to_dict() for d in defects]})

    @app.route("/api/tqm/fmea", methods=["GET"])
    def tqm_fmea():
        fmea_items = tqm_service.get_all_fmea()
        return jsonify({
            "success": True,
            "items": [item.to_dict() for item in fmea_items],
        })

    @app.route("/api/tqm/pdca", methods=["GET"])
    def tqm_pdca():
        pdca_items = tqm_service.get_all_pdca()
        return jsonify({
            "success": True,
            "items": [item.to_dict() for item in pdca_items],
        })

    @app.route("/api/tqm/sipoc", methods=["GET"])
    def tqm_sipoc():
        sipoc_data = tqm_service.get_sipoc_data()
        return jsonify({"success": True, "sipoc": sipoc_data})

    @app.route("/api/tqm/fishbone", methods=["GET"])
    def tqm_fishbone():
        fishbone_data = tqm_service.get_fishbone_data()
        return jsonify({"success": True, "fishbone": fishbone_data})

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)
