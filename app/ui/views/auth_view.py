"""Authentication View: Modern Enterprise Sign In and Sign Up interface with persistent user storage."""

from typing import Callable, Optional
import customtkinter as ctk

from app.models.user import User
from app.services.auth_service import auth_service
from app.ui.theme import THEME, FONTS


class AuthWindow(ctk.CTk):
    """Standalone modern enterprise authentication window for Login and Registration."""

    def __init__(self, on_login_success: Callable[[User], None]):
        super().__init__()

        self.on_login_success = on_login_success

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Inventory Management System — Access Control")
        self.geometry("520x680")
        self.minsize(480, 620)
        self.resizable(False, False)
        self.configure(fg_color="#0B0F19")

        # Center on screen
        self.update_idletasks()
        try:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            x = (screen_w - 520) // 2
            y = (screen_h - 680) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self.current_mode = "login"  # 'login' or 'signup'
        self.show_password = False

        self._build_ui()

    def _build_ui(self):
        # Background Container Card
        self.card = ctk.CTkFrame(
            self,
            fg_color="#131B2E",
            corner_radius=12,
            border_width=1,
            border_color="#1E293B",
        )
        self.card.pack(fill="both", expand=True, padx=24, pady=24)

        # 1. Header Branding
        brand_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(24, 16))

        logo_lbl = ctk.CTkLabel(
            brand_frame,
            text="📦",
            font=("Segoe UI Emoji", 36),
        )
        logo_lbl.pack(pady=(0, 4))

        title_lbl = ctk.CTkLabel(
            brand_frame,
            text="Inventory Management System",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        )
        title_lbl.pack()

        sub_lbl = ctk.CTkLabel(
            brand_frame,
            text="Enterprise Inventory Control & Auditing Platform",
            font=FONTS["small"],
            text_color="#94A3B8",
        )
        sub_lbl.pack(pady=(2, 0))

        # Mode Tab Switcher (Sign In vs Sign Up)
        self.mode_switcher = ctk.CTkSegmentedButton(
            self.card,
            values=["Sign In", "Create Account"],
            font=FONTS["body_bold"],
            selected_color=THEME["primary"],
            selected_hover_color=THEME["primary_hover"],
            unselected_color="#1E293B",
            unselected_hover_color="#334155",
            text_color="#F8FAFC",
            height=36,
            command=self._on_mode_change,
        )
        self.mode_switcher.set("Sign In")
        self.mode_switcher.pack(fill="x", padx=28, pady=(8, 12))

        # Error / Success Message Banner
        self.msg_frame = ctk.CTkFrame(self.card, corner_radius=6)
        self.lbl_msg = ctk.CTkLabel(
            self.msg_frame,
            text="",
            font=FONTS["small_bold"],
            wraplength=420,
            justify="center",
        )
        self.lbl_msg.pack(fill="x", padx=12, pady=6)

        # Dynamic Form Container
        self.form_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        self._render_login_form()

    def _show_message(self, text: str, is_error: bool = True):
        self.lbl_msg.configure(
            text=text,
            text_color="#FCA5A5" if is_error else "#86EFAC",
        )
        self.msg_frame.configure(
            fg_color="#450A0A" if is_error else "#052E16",
            border_width=1,
            border_color="#DC2626" if is_error else "#16A34A",
        )
        self.msg_frame.pack(fill="x", padx=28, pady=(0, 10), before=self.form_container)

    def _hide_message(self):
        self.msg_frame.pack_forget()

    def _on_mode_change(self, value: str):
        self._hide_message()
        if value == "Sign In":
            self.current_mode = "login"
            self._render_login_form()
        else:
            self.current_mode = "signup"
            self._render_signup_form()

    # -------------------------------------------------------------------------
    # LOGIN FORM
    # -------------------------------------------------------------------------
    def _render_login_form(self):
        for child in self.form_container.winfo_children():
            child.destroy()

        # Username
        ctk.CTkLabel(
            self.form_container,
            text="Username or Email",
            font=FONTS["small_bold"],
            text_color="#CBD5E1",
            anchor="w",
        ).pack(fill="x", pady=(4, 2))

        self.login_user_entry = ctk.CTkEntry(
            self.form_container,
            placeholder_text="e.g. admin or manager",
            height=38,
            font=FONTS["body"],
            fg_color="#0F172A",
            border_color="#334155",
            text_color="#F8FAFC",
        )
        self.login_user_entry.pack(fill="x", pady=(0, 12))
        self.login_user_entry.insert(0, "admin")  # Pre-fill for instant convenience

        # Password
        ctk.CTkLabel(
            self.form_container,
            text="Password",
            font=FONTS["small_bold"],
            text_color="#CBD5E1",
            anchor="w",
        ).pack(fill="x", pady=(2, 2))

        pwd_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(0, 16))

        self.login_pwd_entry = ctk.CTkEntry(
            pwd_frame,
            placeholder_text="Enter your password",
            show="*",
            height=38,
            font=FONTS["body"],
            fg_color="#0F172A",
            border_color="#334155",
            text_color="#F8FAFC",
        )
        self.login_pwd_entry.pack(side="left", fill="x", expand=True)
        self.login_pwd_entry.insert(0, "admin123")
        self.login_pwd_entry.bind("<Return>", lambda _: self._handle_login())

        # Toggle Show Password button
        self.btn_toggle_pwd = ctk.CTkButton(
            pwd_frame,
            text="👁️",
            width=38,
            height=38,
            fg_color="#1E293B",
            hover_color="#334155",
            command=self._toggle_password_visibility,
        )
        self.btn_toggle_pwd.pack(side="right", padx=(6, 0))

        # Sign In Button
        btn_signin = ctk.CTkButton(
            self.form_container,
            text="Sign In to System",
            font=FONTS["body_bold"],
            fg_color=THEME["primary"],
            hover_color=THEME["primary_hover"],
            height=40,
            corner_radius=6,
            command=self._handle_login,
        )
        btn_signin.pack(fill="x", pady=(4, 16))

        # Demo Credentials Helper Card with 1-Click Autofill Buttons
        demo_card = ctk.CTkFrame(
            self.form_container,
            fg_color="#0F172A",
            corner_radius=8,
            border_width=1,
            border_color="#1E293B",
        )
        demo_card.pack(fill="x", pady=(4, 8), ipadx=6, ipady=6)

        ctk.CTkLabel(
            demo_card,
            text="🔑 PRE-CONFIGURED DEMO ACCOUNTS (1-CLICK AUTOFILL)",
            font=FONTS["small_bold"],
            text_color="#38BDF8",
            anchor="w",
        ).pack(fill="x", padx=10, pady=(4, 6))

        demo_accounts = [
            ("Admin", "admin", "admin123", "#38BDF8"),
            ("Manager", "manager", "manager123", "#A78BFA"),
            ("Staff", "staff", "staff123", "#34D399"),
        ]

        for role_name, u_name, p_word, color in demo_accounts:
            row = ctk.CTkFrame(demo_card, fg_color="#131B2E", corner_radius=6)
            row.pack(fill="x", padx=8, pady=3, ipadx=4, ipady=3)

            # Role badge tag
            tag = ctk.CTkLabel(
                row,
                text=f" {role_name} ",
                font=FONTS["small_bold"],
                fg_color=color,
                text_color="#0F172A",
                corner_radius=4,
                width=58,
                height=22,
            )
            tag.pack(side="left", padx=(6, 8))

            # Username & Password label
            lbl_creds = ctk.CTkLabel(
                row,
                text=f"{u_name}  •  pass: {p_word}",
                font=FONTS["small"],
                text_color="#CBD5E1",
            )
            lbl_creds.pack(side="left", padx=2)

            # "⚡ Use" Button
            btn_use = ctk.CTkButton(
                row,
                text="⚡ Use",
                font=FONTS["small_bold"],
                fg_color=THEME["primary"],
                hover_color=THEME["primary_hover"],
                text_color="#FFFFFF",
                width=58,
                height=24,
                corner_radius=4,
                command=lambda u=u_name, p=p_word, r=role_name: self._autofill_demo(u, p, r),
            )
            btn_use.pack(side="right", padx=(0, 6))

    def _autofill_demo(self, username: str, password: str, role: str):
        """Autofills selected demo credentials into the input fields."""
        self.login_user_entry.delete(0, "end")
        self.login_user_entry.insert(0, username)

        self.login_pwd_entry.delete(0, "end")
        self.login_pwd_entry.insert(0, password)

        self._show_message(f"Autofilled {role} credentials (@{username}). Click 'Sign In' or press Enter to login!", is_error=False)
        self.login_pwd_entry.focus_set()

    def _toggle_password_visibility(self):
        self.show_password = not self.show_password
        show_char = "" if self.show_password else "*"
        self.login_pwd_entry.configure(show=show_char)

    def _handle_login(self):
        self._hide_message()
        username = self.login_user_entry.get().strip()
        password = self.login_pwd_entry.get()

        if not username or not password:
            self._show_message("Please enter both username and password.", is_error=True)
            return

        success, msg, user = auth_service.authenticate(username, password)
        if success and user:
            self._show_message("Login successful! Loading dashboard...", is_error=False)
            self.after(300, lambda: self._complete_login(user))
        else:
            self._show_message(msg or "Invalid username or password.", is_error=True)

    def _complete_login(self, user: User):
        self.destroy()
        self.on_login_success(user)

    # -------------------------------------------------------------------------
    # SIGN UP FORM
    # -------------------------------------------------------------------------
    def _render_signup_form(self):
        for child in self.form_container.winfo_children():
            child.destroy()

        scroll = ctk.CTkScrollableFrame(self.form_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Full Name
        ctk.CTkLabel(scroll, text="Full Name *", font=FONTS["small_bold"], text_color="#CBD5E1", anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_name = ctk.CTkEntry(scroll, placeholder_text="e.g. Rahul Sharma", height=34, font=FONTS["body"], fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.reg_name.pack(fill="x", pady=(0, 8))

        # Username
        ctk.CTkLabel(scroll, text="Username * (Alphanumeric, min 3 chars)", font=FONTS["small_bold"], text_color="#CBD5E1", anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_user = ctk.CTkEntry(scroll, placeholder_text="e.g. rahul_s", height=34, font=FONTS["body"], fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.reg_user.pack(fill="x", pady=(0, 8))

        # Email
        ctk.CTkLabel(scroll, text="Email Address", font=FONTS["small_bold"], text_color="#CBD5E1", anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_email = ctk.CTkEntry(scroll, placeholder_text="e.g. rahul@company.com", height=34, font=FONTS["body"], fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.reg_email.pack(fill="x", pady=(0, 8))

        # Role selection
        ctk.CTkLabel(scroll, text="Assigned System Role *", font=FONTS["small_bold"], text_color="#CBD5E1", anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_role = ctk.CTkOptionMenu(
            scroll,
            values=["Staff", "Manager", "Admin"],
            font=FONTS["body"],
            fg_color="#0F172A",
            button_color=THEME["secondary"],
            button_hover_color=THEME["secondary_hover"],
            text_color="#F8FAFC",
            height=34,
        )
        self.reg_role.set("Staff")
        self.reg_role.pack(fill="x", pady=(0, 8))

        # Password
        ctk.CTkLabel(scroll, text="Password * (Minimum 6 characters)", font=FONTS["small_bold"], text_color="#CBD5E1", anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_pwd = ctk.CTkEntry(scroll, placeholder_text="Create secure password", show="*", height=34, font=FONTS["body"], fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.reg_pwd.pack(fill="x", pady=(0, 8))

        # Confirm Password
        ctk.CTkLabel(scroll, text="Confirm Password *", font=FONTS["small_bold"], text_color="#CBD5E1", anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_pwd_confirm = ctk.CTkEntry(scroll, placeholder_text="Re-type password", show="*", height=34, font=FONTS["body"], fg_color="#0F172A", border_color="#334155", text_color="#F8FAFC")
        self.reg_pwd_confirm.pack(fill="x", pady=(0, 14))

        # Create Account Button
        btn_create = ctk.CTkButton(
            scroll,
            text="Create New User Account",
            font=FONTS["body_bold"],
            fg_color=THEME["success"],
            hover_color=THEME["success_hover"],
            height=38,
            corner_radius=6,
            command=self._handle_signup,
        )
        btn_create.pack(fill="x", pady=(0, 10))

    def _handle_signup(self):
        self._hide_message()

        full_name = self.reg_name.get().strip()
        username = self.reg_user.get().strip()
        email = self.reg_email.get().strip() or None
        role = self.reg_role.get().strip()
        pwd = self.reg_pwd.get()
        pwd_confirm = self.reg_pwd_confirm.get()

        if not full_name or not username or not pwd:
            self._show_message("Please fill in all mandatory fields (*).", is_error=True)
            return

        if pwd != pwd_confirm:
            self._show_message("Passwords do not match. Please re-type carefully.", is_error=True)
            return

        success, msg, new_user = auth_service.register_user(
            username=username,
            password=pwd,
            full_name=full_name,
            email=email,
            role=role,
        )

        if not success:
            self._show_message(msg, is_error=True)
            return

        # Successfully registered: show success and switch to login tab
        self._show_message("Account created successfully! Please sign in with your credentials.", is_error=False)
        self.mode_switcher.set("Sign In")
        self.current_mode = "login"
        self._render_login_form()
        self.login_user_entry.delete(0, "end")
        self.login_user_entry.insert(0, username)
        self.login_pwd_entry.delete(0, "end")
        self.login_pwd_entry.focus_set()
