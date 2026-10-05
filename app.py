import streamlit as st
import subprocess
import tempfile
import os
import io
import contextlib
import ast
import re
import html
import builtins
import sys

from supabase import create_client


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Code Visualizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

def get_supabase():
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]

        return create_client(
            supabase_url,
            supabase_key
        )

    except Exception:
        return None


supabase = get_supabase()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "authenticated": False,
    "user_email": "",
    "auth_page": "login",

    "output": "",
    "error": "",
    "view": "home",
    "code": "",
    "program_input": "",
    "trace": []
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CHECK EXISTING SUPABASE SESSION
# =========================================================

if supabase is not None:

    try:
        current_session = supabase.auth.get_session()

        if current_session is not None:

            if current_session.user is not None:

                st.session_state.authenticated = True

                st.session_state.user_email = (
                    current_session.user.email or ""
                )

    except Exception:
        pass


# =========================================================
# PROFESSIONAL CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f8fc;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: #172033;
        margin-top: 10px;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .card {
        background: white;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 5px 20px rgba(0,0,0,.05);
        margin-bottom: 20px;
    }

    .auth-card {
        background: white;
        padding: 35px;
        border-radius: 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 35px rgba(0,0,0,.08);
        max-width: 520px;
        margin: 40px auto;
    }

    .auth-title {
        text-align: center;
        color: #172033;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .auth-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #172033;
        margin-bottom: 12px;
    }

    .visual-card {
        background: white;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        text-align: center;
        min-height: 180px;
        box-shadow: 0 4px 15px rgba(0,0,0,.04);
    }

    .step {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 16px;
        margin: 10px 0;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,.04);
    }

    .assistant {
        background: white;
        border-left: 5px solid #2563eb;
        padding: 18px;
        border-radius: 10px;
        margin-top: 10px;
    }

    .flow {
        background: #ecfdf5;
        border: 2px solid #10b981;
        padding: 15px;
        margin: 10px auto;
        width: 80%;
        text-align: center;
        border-radius: 12px;
    }

    .decision {
        background: #fff7ed;
        border: 2px solid #f97316;
        padding: 15px;
        margin: 10px auto;
        width: 80%;
        text-align: center;
        border-radius: 12px;
    }

    .startend {
        background: #ede9fe;
        border: 2px solid #7c3aed;
        padding: 15px;
        margin: 10px auto;
        width: 60%;
        text-align: center;
        border-radius: 35px;
        font-weight: bold;
    }

    .arrow {
        text-align: center;
        font-size: 25px;
        color: #64748b;
        font-weight: bold;
    }

    .user-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# AUTHENTICATION FUNCTIONS
# =========================================================

def login_user(email, password):

    if supabase is None:
        return False, "Supabase configuration is missing."

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )

        if response.user:

            st.session_state.authenticated = True

            st.session_state.user_email = (
                response.user.email or email
            )

            return True, ""

        return False, "Login failed."

    except Exception as e:

        return False, str(e)


def signup_user(email, password):

    if supabase is None:
        return False, "Supabase configuration is missing."

    try:

        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )

        if response.user:

            if response.session:

                st.session_state.authenticated = True

                st.session_state.user_email = (
                    response.user.email or email
                )

                return True, "Account created successfully."

            return True, (
                "Account created. "
                "Please check your email and verify your account."
            )

        return False, "Account creation failed."

    except Exception as e:

        return False, str(e)


def logout_user():

    if supabase is not None:

        try:
            supabase.auth.sign_out()

        except Exception:
            pass

    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.output = ""
    st.session_state.error = ""
    st.session_state.trace = []
    st.session_state.view = "home"

    st.rerun()


# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if not st.session_state.authenticated:

    st.markdown(
        '<div class="auth-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="auth-title">🧠 Smart Code Visualizer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="auth-subtitle">'
        'Understand Code Through Visualization'
        '</div>',
        unsafe_allow_html=True
    )

    if supabase is None:

        st.error(
            "Supabase is not configured yet. "
            "Create .streamlit/secrets.toml with "
            "SUPABASE_URL and SUPABASE_KEY."
        )

    if st.session_state.auth_page == "login":

        st.markdown("### 🔐 Login")

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.button(
            "🔐 Login",
            type="primary",
            use_container_width=True
        )

        if login_button:

            if not email.strip():

                st.warning("Please enter your email.")

            elif not password:

                st.warning("Please enter your password.")

            else:

                with st.spinner("Logging in..."):

                    success, message = login_user(
                        email.strip(),
                        password
                    )

                if success:

                    st.success("Login successful!")

                    st.rerun()

                else:

                    st.error(
                        "Login failed. "
                        + message
                    )

        st.divider()

        st.markdown(
            "<div style='text-align:center;'>"
            "Don't have an account?"
            "</div>",
            unsafe_allow_html=True
        )

        if st.button(
            "Create New Account",
            use_container_width=True
        ):

            st.session_state.auth_page = "signup"

            st.rerun()

        st.divider()

        st.markdown(
            "<div style='text-align:center;color:#64748b;'>"
            "Google login can be enabled after configuring "
            "Google OAuth in Supabase."
            "</div>",
            unsafe_allow_html=True
        )

    else:

        st.markdown("### 📝 Create Account")

        signup_email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            key="signup_password"
        )

        signup_confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm"
        )

        signup_button = st.button(
            "🚀 Create Account",
            type="primary",
            use_container_width=True
        )

        if signup_button:

            if not signup_email.strip():

                st.warning("Please enter your email.")

            elif not signup_password:

                st.warning("Please enter a password.")

            elif len(signup_password) < 6:

                st.warning(
                    "Password should contain at least 6 characters."
                )

            elif signup_password != signup_confirm:

                st.error(
                    "Passwords do not match."
                )

            else:

                with st.spinner("Creating your account..."):

                    success, message = signup_user(
                        signup_email.strip(),
                        signup_password
                    )

                if success:

                    if st.session_state.authenticated:

                        st.success(
                            "Account created successfully!"
                        )

                        st.rerun()

                    else:

                        st.success(message)

                else:

                    st.error(
                        "Account creation failed. "
                        + message
                    )

        st.divider()

        if st.button(
            "← Back to Login",
            use_container_width=True
        ):

            st.session_state.auth_page = "login"

            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.stop()


# =========================================================
# CODE ANALYSIS HELPERS
# =========================================================

def set_view(view):

    st.session_state.view = view


def clean_line(line):

    line = line.strip()

    line = re.sub(
        r"//.*$",
        "",
        line
    )

    if not line.startswith("#"):

        line = re.sub(
            r"#.*$",
            "",
            line
        )

    return line.strip()


def get_lines(source_code):

    result = []

    for raw in source_code.splitlines():

        line = clean_line(raw)

        if line and line not in ("{", "}"):

            result.append(line)

    return result


def line_type(line):

    s = line.lower().strip()

    if re.match(
        r"^(if\s*\(|if\s+)",
        s
    ) or s.startswith("elif "):

        return "condition"

    if re.match(
        r"^else\b",
        s
    ):

        return "else"

    if re.match(
        r"^(for\s*\(|for\s+|while\s*\(|while\s+)",
        s
    ):

        return "loop"

    if any(
        x in s
        for x in (
            "printf",
            "cout",
            "system.out.print",
            "print("
        )
    ):

        return "output"

    if any(
        x in s
        for x in (
            "scanf",
            "cin",
            "input("
        )
    ):

        return "input"

    if "=" in line and "==" not in line and "!=" not in line:

        return "assignment"

    return "statement"


def explain_line(line, kind):

    if kind == "condition":

        return (
            f"Check the condition: {line}"
        )

    if kind == "else":

        return (
            "If the previous condition is false, "
            "execute this branch."
        )

    if kind == "loop":

        return (
            f"Repeat the loop according to: {line}"
        )

    if kind == "input":

        return (
            f"Read input from the user using: {line}"
        )

    if kind == "output":

        return (
            f"Display the result using: {line}"
        )

    if kind == "assignment":

        return (
            "Evaluate the expression on the right-hand side, "
            "then store/update the result in the variable: "
            + line
        )

    return (
        "Execute this statement in order. "
        "Its exact effect depends on the expression "
        "and current variable values: "
        + line
    )


def make_algorithm(lines):

    return [
        explain_line(
            line,
            line_type(line)
        )
        for line in lines
    ]


def make_detailed_steps(lines, output):

    steps = []

    for i, line in enumerate(lines, 1):

        kind = line_type(line)

        if kind == "condition":

            title = f"Step {i}: Condition check"

            detail = (
                f"The program reaches `{line}` "
                "and checks the condition to decide "
                "which branch should run."
            )

        elif kind == "else":

            title = f"Step {i}: Else branch"

            detail = (
                "This branch runs when the previous "
                "condition is false."
            )

        elif kind == "loop":

            title = f"Step {i}: Loop"

            detail = (
                f"The program repeats according to `{line}`."
            )

        elif kind == "input":

            title = f"Step {i}: Input"

            detail = (
                f"The program reads a value from the user "
                f"using `{line}`."
            )

        elif kind == "output":

            title = f"Step {i}: Output"

            detail = (
                f"The program executes `{line}` "
                "to display a result."
            )

        elif kind == "assignment":

            title = f"Step {i}: Value update"

            detail = (
                f"The program creates or updates a value "
                f"using `{line}`."
            )

        else:

            title = f"Step {i}: Statement"

            detail = (
                f"The program executes `{line}`."
            )

        steps.append(
            (
                title,
                detail
            )
        )

    if output.strip():

        steps.append(
            (
                "Final Result",
                "The program finished and produced:\n"
                + output.strip()
            )
        )

    return steps


# =========================================================
# PROGRAM EXECUTION
# =========================================================

PYTHON_TRACE = []


def format_variables(local_vars):

    visible = {}

    for name, value in local_vars.items():

        if name.startswith("__"):
            continue

        if name == "input":
            continue

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
                type(None),
                list,
                tuple,
                dict,
                set
            )
        ):

            try:

                rendered = repr(value)

                visible[name] = (
                    rendered[:250]
                    + (
                        "..."
                        if len(rendered) > 250
                        else ""
                    )
                )

            except Exception:

                visible[name] = (
                    f"<{type(value).__name__}>"
                )

    return visible


def run_python(source_code, user_input):

    global PYTHON_TRACE

    PYTHON_TRACE = []

    output = io.StringIO()

    values = iter(
        user_input.splitlines()
    )

    def custom_input(prompt=""):

        try:

            value = next(values)

        except StopIteration:

            raise EOFError(
                "No more input was provided. "
                "Enter the required values "
                "in the Program Input box."
            )

        if prompt:

            output.write(prompt)

        return value

    original_input = builtins.input

    original_trace = sys.gettrace()

    def trace_execution(
        frame,
        event,
        arg
    ):

        if (
            event == "line"
            and frame.f_code.co_filename
            == "<user_code>"
        ):

            line_no = frame.f_lineno

            source_lines = (
                source_code.splitlines()
            )

            source_line = (
                source_lines[line_no - 1].strip()
                if 0 < line_no <= len(source_lines)
                else ""
            )

            PYTHON_TRACE.append(
                {
                    "line": line_no,
                    "source": source_line,
                    "variables": format_variables(
                        frame.f_locals
                    )
                }
            )

        return trace_execution

    try:

        ast.parse(source_code)

        builtins.input = custom_input

        with contextlib.redirect_stdout(output):

            sys.settrace(
                trace_execution
            )

            exec(
                compile(
                    source_code,
                    "<user_code>",
                    "exec"
                ),
                {
                    "__name__": "__main__"
                }
            )

        return (
            output.getvalue(),
            ""
        )

    except Exception as e:

        return (
            "",
            f"{type(e).__name__}: {e}"
        )

    finally:

        sys.settrace(
            original_trace
        )

        builtins.input = original_input


def run_compiled(
    language,
    source_code,
    user_input
):

    if language == "C":

        compiler = "gcc"
        filename = "program.c"

    elif language == "C++":

        compiler = "g++"
        filename = "program.cpp"

    else:

        compiler = "javac"
        filename = "Main.java"

    with tempfile.TemporaryDirectory() as folder:

        source_path = os.path.join(
            folder,
            filename
        )

        with open(
            source_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                source_code
            )

        try:

            if language in ("C", "C++"):

                executable = os.path.join(
                    folder,
                    "program"
                )

                compile_result = subprocess.run(
                    [
                        compiler,
                        source_path,
                        "-o",
                        executable
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if compile_result.returncode != 0:

                    return (
                        "",
                        compile_result.stderr
                    )

                result = subprocess.run(
                    [executable],
                    input=user_input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                return (
                    result.stdout,
                    result.stderr
                )

            compile_result = subprocess.run(
                [
                    compiler,
                    source_path
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if compile_result.returncode != 0:

                return (
                    "",
                    compile_result.stderr
                )

            result = subprocess.run(
                [
                    "java",
                    "-cp",
                    folder,
                    "Main"
                ],
                input=user_input,
                capture_output=True,
                text=True,
                timeout=5
            )

            return (
                result.stdout,
                result.stderr
            )

        except FileNotFoundError:

            if language == "C":

                return (
                    "",
                    "GCC is not installed "
                    "or is not available in PATH."
                )

            if language == "C++":

                return (
                    "",
                    "G++ is not installed "
                    "or is not available in PATH."
                )

            return (
                "",
                "Java JDK is not installed "
                "or java/javac is not available in PATH."
            )

        except subprocess.TimeoutExpired:

            return (
                "",
                "Program took too long to finish. "
                "Check for an infinite loop."
            )

        except Exception as e:

            return (
                "",
                f"{type(e).__name__}: {e}"
            )


def run_code(
    language,
    source_code,
    user_input
):

    if language == "Python":

        return run_python(
            source_code,
            user_input
        )

    return run_compiled(
        language,
        source_code,
        user_input
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '🧠 Smart Code Visualizer'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Understand Code Through Visualization'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🧠 Smart Code")
    st.markdown("### Visualizer")

    st.divider()

    st.markdown("### 👤 Account")

    st.markdown(
        f"""
        <div class="user-box">
        <b>Logged in as</b><br>
        {html.escape(st.session_state.user_email)}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout_user()

    st.divider()

    st.markdown("### Navigation")

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):

        set_view("home")

    if st.button(
        "💻 Code Editor",
        use_container_width=True
    ):

        set_view("editor")

    if st.button(
        "▶ Run Code",
        use_container_width=True
    ):

        set_view("run")

    if st.button(
        "📊 Visualize",
        use_container_width=True
    ):

        set_view("visualize")

    if st.button(
        "🔄 Flowchart",
        use_container_width=True
    ):

        set_view("flowchart")

    if st.button(
        "📝 Algorithm",
        use_container_width=True
    ):

        set_view("algorithm")

    if st.button(
        "▶️ Step-by-Step",
        use_container_width=True
    ):

        set_view("steps")

    if st.button(
        "🧪 Lab Assistance",
        use_container_width=True
    ):

        set_view("lab")

    st.divider()

    st.markdown("### Supported Languages")

    st.write("🐍 Python")
    st.write("🔵 C")
    st.write("🔷 C++")
    st.write("☕ Java")

    st.divider()

    st.info(
        "Write code → Give input → Run → "
        "Choose visualization → Understand each step."
    )


# =========================================================
# CODE EDITOR + INPUT
# =========================================================

left, right = st.columns(
    [1.5, 1]
)


with left:

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        '1️⃣ Select Programming Language'
        '</div>',
        unsafe_allow_html=True
    )

    language = st.selectbox(
        "Language",
        [
            "Python",
            "C",
            "C++",
            "Java"
        ]
    )

    st.markdown(
        '<div class="section-title">'
        '2️⃣ Enter Your Code'
        '</div>',
        unsafe_allow_html=True
    )

    code = st.text_area(
        "Code Editor",
        value=st.session_state.code,
        height=300,
        placeholder="Write or paste your code here..."
    )

    st.session_state.code = code

    st.markdown(
        '<div class="section-title">'
        '3️⃣ Program Input'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "If your program uses input(), scanf(), cin, "
        "or Scanner, enter values here — one value per line."
    )

    program_input = st.text_area(
        "Input",
        value=st.session_state.program_input,
        height=110,
        placeholder=""
    )

    st.session_state.program_input = program_input

    run_button = st.button(
        "▶ RUN CODE",
        type="primary",
        use_container_width=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# OUTPUT
# =========================================================

with right:

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        '📤 Program Output'
        '</div>',
        unsafe_allow_html=True
    )

    if run_button:

        st.session_state.output = ""
        st.session_state.error = ""
        st.session_state.trace = []

        if not code.strip():

            st.session_state.error = (
                "Please enter your code first."
            )

        else:

            with st.spinner(
                "Running your program..."
            ):

                out, err = run_code(
                    language,
                    code,
                    program_input
                )

            st.session_state.output = out
            st.session_state.error = err

            if language == "Python":

                st.session_state.trace = list(
                    PYTHON_TRACE
                )

            else:

                st.session_state.trace = []

    if st.session_state.error:

        st.error("Program Error")

        st.code(
            st.session_state.error,
            language="text"
        )

    elif st.session_state.output:

        st.success(
            "✓ Code executed successfully"
        )

        st.code(
            st.session_state.output,
            language="text"
        )

    else:

        st.info(
            "Run your program to see the output."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# VISUALIZATION OPTIONS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '4️⃣ Choose Visualization Method'
    '</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)


with c1:

    st.markdown(
        '<div class="visual-card">'
        '<div style="font-size:38px;">🔄</div>'
        '<h3>Flowchart</h3>'
        '<p>See the logical flow of your program.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "VIEW FLOWCHART",
        use_container_width=True
    ):

        set_view("flowchart")


with c2:

    st.markdown(
        '<div class="visual-card">'
        '<div style="font-size:38px;">📝</div>'
        '<h3>Algorithm</h3>'
        '<p>Convert code into simple human-readable steps.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "VIEW ALGORITHM",
        use_container_width=True
    ):

        set_view("algorithm")


with c3:

    st.markdown(
        '<div class="visual-card">'
        '<div style="font-size:38px;">▶️</div>'
        '<h3>Step-by-Step</h3>'
        '<p>Understand how each line contributes to execution.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "VIEW STEPS",
        use_container_width=True
    ):

        set_view("steps")


# =========================================================
# LAB ASSISTANT
# =========================================================

if st.session_state.error:

    st.header("🧪 Lab Assistant")

    error_text = (
        st.session_state.error.lower()
    )

    if "syntaxerror" in error_text:

        explanation = (
            "There is a syntax problem. "
            "Check brackets, quotes, colons "
            "and the reported line."
        )

    elif "indentationerror" in error_text:

        explanation = (
            "The indentation is incorrect. "
            "Check the spaces inside if, loops "
            "and functions."
        )

    elif "eoferror" in error_text:

        explanation = (
            "The program expected more input. "
            "Add the required input values "
            "in the Program Input box."
        )

    elif "java jdk" in error_text:

        explanation = (
            "Java JDK is not available in the "
            "deployment environment. Check packages.txt "
            "and the Streamlit build logs."
        )

    elif "cannot find symbol" in error_text:

        explanation = (
            "Java cannot find a variable, method "
            "or class. Check spelling and declarations."
        )

    else:

        explanation = (
            "Read the error message above and check "
            "the indicated line first."
        )

    st.markdown(
        f"""
        <div class="assistant">
        <b>💡 What went wrong?</b>
        <br><br>
        {html.escape(explanation)}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# VISUALIZATION DISPLAY
# =========================================================

st.divider()


if not code.strip():

    st.info(
        "Enter code above, provide input if required, "
        "and choose a visualization method."
    )

else:

    lines = get_lines(code)

    # =====================================================
    # FLOWCHART
    # =====================================================

    if st.session_state.view == "flowchart":

        st.header(
            "🔄 Program Flowchart"
        )

        st.caption(
            f"Language: {language}"
        )

        st.markdown(
            '<div class="startend">'
            '🟢 START'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="arrow">↓</div>',
            unsafe_allow_html=True
        )

        for line in lines:

            kind = line_type(line)

            safe = html.escape(line)

            if kind in (
                "condition",
                "else"
            ):

                st.markdown(
                    f"""
                    <div class="decision">
                    🔷 {kind.upper()}
                    <br><br>
                    {safe}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="flow">
                    {safe}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                '<div class="arrow">↓</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="startend">'
            '🔴 END'
            '</div>',
            unsafe_allow_html=True
        )


    # =====================================================
    # ALGORITHM
    # =====================================================

    elif st.session_state.view == "algorithm":

        st.header(
            "📝 Generated Algorithm"
        )

        st.caption(
            f"Generated from {language} code"
        )

        steps = make_algorithm(
            lines
        )

        if not steps:

            st.info(
                "No code steps found."
            )

        else:

            for i, step in enumerate(
                steps,
                1
            ):

                st.markdown(
                    f"""
                    <div class="step">
                    <b>Step {i}</b>
                    <br>
                    {html.escape(step)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # =====================================================
    # STEP BY STEP
    # =====================================================

    elif st.session_state.view == "steps":

        st.header(
            "▶️ Step-by-Step Program Logic"
        )

        st.caption(
            "Each source-code line is explained "
            "in simple language. The final output "
            "is shown at the end."
        )

        detailed_steps = make_detailed_steps(
            lines,
            st.session_state.output
        )

        st.subheader(
            "1. Line-by-line explanation"
        )

        st.caption(
            "The explanation describes each source line. "
            "For Python, after you run the program, "
            "the runtime trace below also shows the line "
            "reached and variable values available at that moment. "
            "For C, C++, and Java, the explanation is based "
            "on source-code analysis."
        )

        if not detailed_steps:

            st.info(
                "No code steps found."
            )

        else:

            for title, detail in detailed_steps:

                detail_html = (
                    html.escape(detail)
                    .replace(
                        "\n",
                        "<br>"
                    )
                )

                st.markdown(
                    f"""
                    <div class="step">
                    <b>{html.escape(title)}</b>
                    <br><br>
                    {detail_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.subheader(
            "2. Execution trace and variable values"
        )

        if language == "Python":

            if st.session_state.trace:

                st.write(
                    "Each entry records a Python source line "
                    "when execution reached it. Variable values "
                    "are the values visible at that point."
                )

                for index, event in enumerate(
                    st.session_state.trace,
                    1
                ):

                    vars_text = event[
                        "variables"
                    ]

                    with st.expander(
                        f"Execution {index} — "
                        f"line {event['line']}: "
                        f"{event['source'] or '(blank line)'}"
                    ):

                        if vars_text:

                            st.markdown(
                                "**Variable values at this point**"
                            )

                            for (
                                var_name,
                                var_value
                            ) in vars_text.items():

                                st.code(
                                    f"{var_name} = {var_value}",
                                    language="python"
                                )

                        else:

                            st.write(
                                "No user variables have "
                                "been created yet."
                            )

            else:

                st.info(
                    "Run a Python program first "
                    "to generate its execution trace."
                )

        else:

            st.info(
                f"For {language}, this version explains "
                "every non-empty source line and shows the "
                "final output, but it does not capture live "
                "variable values for compiled languages."
            )


    # =====================================================
    # LAB
    # =====================================================

    elif st.session_state.view == "lab":

        st.header(
            "🧪 Lab Assistance"
        )

        if st.session_state.error:

            st.write(
                "Fix the error shown above "
                "and run the program again."
            )

        else:

            st.success(
                "No current program error."
            )

            st.write(
                "Use the Program Input box whenever "
                "your code needs user input."
            )


    # =====================================================
    # HOME
    # =====================================================

    elif st.session_state.view == "home":

        st.success(
            "Welcome! Enter code, provide input if needed, "
            "run it, and choose a visualization."
        )


    # =====================================================
    # EDITOR
    # =====================================================

    elif st.session_state.view == "editor":

        st.info(
            "Use the Code Editor above to write "
            "or paste your program."
        )


    # =====================================================
    # RUN
    # =====================================================

    elif st.session_state.view == "run":

        st.info(
            "Use Program Input for input values, "
            "then click RUN CODE."
        )


    # =====================================================
    # VISUALIZE
    # =====================================================

    elif st.session_state.view == "visualize":

        st.info(
            "Choose Flowchart, Algorithm, "
            "or Step-by-Step below."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🧠 Smart Code Visualizer | Learn by Seeing | "
    "Python • C • C++ • Java"
)