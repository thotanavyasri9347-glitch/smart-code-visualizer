import streamlit as st
import subprocess
import tempfile
import os
import io
import contextlib
import ast
import re
import html

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Code Visualizer",
    page_icon="🧠",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f7f8fc;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #172033;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 18px;
    margin-bottom: 25px;
}

.box {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    margin-bottom: 18px;
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

.assistant {
    background: white;
    border-left: 5px solid #2563eb;
    padding: 18px;
    border-radius: 10px;
    margin-top: 10px;
}

.step {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 16px;
    margin: 10px 0;
    border-radius: 10px;
}

.step-number {
    color: #2563eb;
    font-weight: bold;
    font-size: 18px;
}

.arrow {
    text-align: center;
    font-size: 25px;
    color: #64748b;
}

.success-box {
    background: #ecfdf5;
    border: 2px solid #10b981;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
}

.warning-box {
    background: #fff7ed;
    border: 2px solid #f97316;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
}

.error-box {
    background: #fef2f2;
    border: 2px solid #ef4444;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
}

.info-box {
    background: #eff6ff;
    border: 2px solid #3b82f6;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "code" not in st.session_state:
    st.session_state.code = ""

if "output" not in st.session_state:
    st.session_state.output = ""

if "error" not in st.session_state:
    st.session_state.error = ""

if "view" not in st.session_state:
    st.session_state.view = ""

if "language" not in st.session_state:
    st.session_state.language = "Python"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🧠 Smart Code")
    st.write("### Navigation")

    st.write("🏠 Home")
    st.write("💻 Code Editor")
    st.write("▶ Run Code")
    st.write("📊 Visualize")
    st.write("🧪 Lab Assistance")

    st.divider()

    st.write("### Supported Languages")

    st.write("🐍 Python")
    st.write("🔵 C")
    st.write("🔷 C++")
    st.write("☕ Java")

    st.divider()

    st.info(
        "Write code → Run → Visualize → "
        "Understand the error."
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">🧠 Smart Code Visualizer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Understand Code Through Visualization & Lab Assistance'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# RUN PROGRAM
# =========================================================

def run_program(language, source_code):

    # =====================================================
    # PYTHON
    # =====================================================

    if language == "Python":

        output = io.StringIO()

        try:

            ast.parse(source_code)

            with contextlib.redirect_stdout(output):

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

            return output.getvalue(), ""

        except Exception as e:

            return "", (
                f"{type(e).__name__}: {e}"
            )

    # =====================================================
    # C
    # =====================================================

    if language == "C":

        compiler = "gcc"
        filename = "program.c"

    # =====================================================
    # C++
    # =====================================================

    elif language == "C++":

        compiler = "g++"
        filename = "program.cpp"

    # =====================================================
    # JAVA
    # =====================================================

    else:

        compiler = "javac"
        filename = "Main.java"

        if not re.search(
            r"\bclass\s+Main\b",
            source_code
        ):

            return "", (
                "Java code must contain a class named Main.\n\n"
                "Example:\n\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        System.out.println(\"Hello\");\n"
                "    }\n"
                "}"
            )

    # =====================================================
    # TEMPORARY DIRECTORY
    # =====================================================

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

            file.write(source_code)

        try:

            # =================================================
            # C / C++
            # =================================================

            if language in ("C", "C++"):

                executable = os.path.join(
                    folder,
                    "program.exe"
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

                    return "", compile_result.stderr

                result = subprocess.run(
                    [executable],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode != 0:

                    return (
                        result.stdout,
                        result.stderr
                    )

                return result.stdout, ""

            # =================================================
            # JAVA
            # =================================================

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

                return "", compile_result.stderr

            result = subprocess.run(
                [
                    "java",
                    "-cp",
                    folder,
                    "Main"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:

                return (
                    result.stdout,
                    result.stderr
                )

            return result.stdout, ""

        except FileNotFoundError:

            if language == "C":

                return "", (
                    "GCC is not installed or "
                    "is not available in PATH."
                )

            elif language == "C++":

                return "", (
                    "G++ is not installed or "
                    "is not available in PATH."
                )

            else:

                return "", (
                    "Java JDK is not installed or "
                    "java/javac is not available in PATH."
                )

        except subprocess.TimeoutExpired:

            return "", (
                "Program took too long to finish. "
                "Check for an infinite loop."
            )

        except Exception as e:

            return "", (
                f"{type(e).__name__}: {e}"
            )


# =========================================================
# CLEAN LINE
# =========================================================

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


# =========================================================
# GET CODE LINES
# =========================================================

def get_lines(source_code):

    result = []

    for line in source_code.splitlines():

        line = clean_line(line)

        if line and line not in ("{", "}"):

            result.append(line)

    return result


# =========================================================
# LINE TYPE
# =========================================================

def line_type(line):

    text = line.lower().strip()

    # IF

    if re.match(
        r"^if\s*(\(|:)",
        text
    ) or text.startswith("if "):

        return "condition"

    # ELSE / ELIF

    if re.match(
        r"^else\b",
        text
    ) or re.match(
        r"^elif\b",
        text
    ):

        return "condition"

    # FOR / WHILE

    if re.match(
        r"^for\b",
        text
    ) or re.match(
        r"^while\b",
        text
    ):

        return "loop"

    # OUTPUT

    if (
        "printf" in text
        or "cout" in text
        or "system.out.print" in text
        or "print(" in text
    ):

        return "output"

    # INPUT

    if (
        "scanf" in text
        or "cin" in text
        or "input(" in text
    ):

        return "input"

    # FUNCTION

    if (
        re.match(r"^def\s+", text)
        or re.match(
            r".*\bvoid\s+\w+\s*\(",
            text
        )
        or re.match(
            r".*\bint\s+\w+\s*\(",
            text
        )
    ):

        return "function"

    # ASSIGNMENT

    if (
        "=" in line
        and "==" not in line
        and "!=" not in line
        and "<=" not in line
        and ">=" not in line
    ):

        return "assignment"

    return "statement"


# =========================================================
# ERROR EXPLANATION
# =========================================================

def explain_error(language, error):

    text = error.lower()

    # =====================================================
    # NAME ERROR
    # =====================================================

    if "nameerror" in text:

        match = re.search(
            r"name ['\"]([^'\"]+)['\"] is not defined",
            error,
            re.IGNORECASE
        )

        if match:

            name = match.group(1)

            return (
                f"### 🔴 Undefined Name: `{name}`\n\n"

                f"**What happened?**\n\n"
                f"The program tried to use `{name}`, "
                f"but Python could not find a variable or "
                f"function with that name.\n\n"

                f"**Why did this happen?**\n\n"
                f"- `{name}` was not defined.\n"
                f"- The variable name may be misspelled.\n"
                f"- The variable may exist in another scope.\n"
                f"- A function may have been called incorrectly.\n\n"

                f"**How to fix it?**\n\n"
                f"1. Check the spelling of `{name}`.\n"
                f"2. Define `{name}` before using it.\n"
                f"3. Check whether the variable is inside the "
                f"correct scope.\n\n"

                f"**Example:**\n\n"
                f"```python\n"
                f"x = 10\n"
                f"print(x)\n"
                f"```\n\n"

                f"Here `x` is defined before it is used."
            )

        return (
            "### 🔴 Name Error\n\n"
            "Python cannot find the variable or function "
            "that your program is trying to use.\n\n"
            "**Check:**\n"
            "- Variable spelling\n"
            "- Function name\n"
            "- Variable declaration\n"
            "- Variable scope"
        )

    # =====================================================
    # SYNTAX ERROR
    # =====================================================

    if "syntaxerror" in text:

        return (
            "### 🔴 Syntax Error\n\n"

            "Python could not understand the structure "
            "of your code.\n\n"

            "**Common causes:**\n"
            "- Missing `:` after if, for, while or function\n"
            "- Missing `)` or `]`\n"
            "- Missing quotation mark\n"
            "- Incorrect Python syntax\n\n"

            "**How to fix it:**\n"
            "Check the line mentioned in the error and "
            "also check the line immediately before it."
        )

    # =====================================================
    # INDENTATION
    # =====================================================

    if "indentationerror" in text:

        return (
            "### 🔴 Indentation Error\n\n"

            "Python uses indentation to identify blocks "
            "of code.\n\n"

            "**Example:**\n\n"

            "```python\n"
            "if x > 10:\n"
            "    print(x)\n"
            "```\n\n"

            "The `print()` statement belongs to the `if` "
            "block, so it must be indented.\n\n"

            "**How to fix it:**\n"
            "Make sure statements inside if, for, while, "
            "functions and classes use consistent indentation."
        )

    # =====================================================
    # TYPE ERROR
    # =====================================================

    if "typeerror" in text:

        return (
            "### 🔴 Type Error\n\n"

            "Your program is trying to perform an operation "
            "using incompatible data types.\n\n"

            "**Example:**\n\n"

            "```python\n"
            "age = 20\n"
            "print(age + \" years\")\n"
            "```\n\n"

            "Here an integer and a string are being combined "
            "incorrectly.\n\n"

            "**How to fix it:**\n"
            "Check the data types of the variables before "
            "performing the operation."
        )

    # =====================================================
    # INDEX ERROR
    # =====================================================

    if "indexerror" in text:

        return (
            "### 🔴 Index Error\n\n"

            "Your program tried to access an index that "
            "does not exist in a list or array.\n\n"

            "**Example:**\n\n"

            "```python\n"
            "numbers = [10, 20, 30]\n"
            "print(numbers[3])\n"
            "```\n\n"

            "Valid indexes are `0`, `1`, and `2`.\n\n"

            "**How to fix it:**\n"
            "Check the length of the list and make sure "
            "the index is within the valid range."
        )

    # =====================================================
    # ZERO DIVISION
    # =====================================================

    if "zerodivisionerror" in text:

        return (
            "### 🔴 Zero Division Error\n\n"

            "Your program is trying to divide a number by zero.\n\n"

            "**Example:**\n\n"

            "```python\n"
            "a = 10\n"
            "b = 0\n"
            "print(a / b)\n"
            "```\n\n"

            "Division by zero is not allowed.\n\n"

            "**How to fix it:**\n"
            "Check the denominator before performing division."
        )

    # =====================================================
    # VALUE ERROR
    # =====================================================

    if "valueerror" in text:

        return (
            "### 🔴 Value Error\n\n"

            "The program received a value that cannot be "
            "used in the requested operation.\n\n"

            "**Example:**\n\n"

            "```python\n"
            "age = int(\"hello\")\n"
            "```\n\n"

            "`hello` cannot be converted into an integer.\n\n"

            "**How to fix it:**\n"
            "Check the input value before converting it."
        )

    # =====================================================
    # ATTRIBUTE ERROR
    # =====================================================

    if "attributeerror" in text:

        return (
            "### 🔴 Attribute Error\n\n"

            "The object you are using does not have the "
            "attribute or method you requested.\n\n"

            "**Check:**\n"
            "- Object type\n"
            "- Method spelling\n"
            "- Whether that method exists for the object"
        )

    # =====================================================
    # FILE NOT FOUND
    # =====================================================

    if "filenotfounderror" in text:

        return (
            "### 🔴 File Not Found Error\n\n"

            "The program tried to open a file that "
            "could not be found.\n\n"

            "**How to fix it:**\n"
            "Check the file name and make sure the file "
            "exists in the expected folder."
        )

    # =====================================================
    # C / C++ SEMICOLON
    # =====================================================

    if (
        "expected ';'" in text
        or "expected ';' before" in text
    ):

        return (
            "### 🔴 Missing Semicolon\n\n"

            "The compiler expected a semicolon `;`.\n\n"

            "**Example:**\n\n"

            "```c\n"
            "int x = 10;\n"
            "```\n\n"

            "Check the current line and the previous line "
            "for a missing semicolon."
        )

    # =====================================================
    # C / C++ UNDECLARED
    # =====================================================

    if "undeclared" in text:

        return (
            "### 🔴 Undeclared Variable\n\n"

            "The program is using a variable that has not "
            "been declared.\n\n"

            "**Example:**\n\n"

            "```c\n"
            "int x = 10;\n"
            "printf(\"%d\", x);\n"
            "```\n\n"

            "Make sure the variable is declared before "
            "using it."
        )

    if "was not declared" in text:

        return (
            "### 🔴 Variable Not Declared\n\n"

            "The compiler cannot find the variable you "
            "are trying to use.\n\n"

            "**Check:**\n"
            "- Variable declaration\n"
            "- Variable spelling\n"
            "- Variable scope"
        )

    # =====================================================
    # JAVA
    # =====================================================

    if "cannot find symbol" in text:

        return (
            "### 🔴 Java: Cannot Find Symbol\n\n"

            "Java cannot find a variable, method or class "
            "used in your program.\n\n"

            "**Possible reasons:**\n"
            "- Misspelled variable name\n"
            "- Missing declaration\n"
            "- Incorrect method name\n"
            "- Missing import\n\n"

            "**How to fix it:**\n"
            "Check the spelling and declaration of the "
            "symbol mentioned by the compiler."
        )

    # =====================================================
    # BRACKET ERROR
    # =====================================================

    if "never closed" in text:

        return (
            "### 🔴 Unclosed Bracket or Parenthesis\n\n"

            "A bracket was opened but was not closed.\n\n"

            "**Check:**\n"
            "- `()` parentheses\n"
            "- `[]` square brackets\n"
            "- `{}` curly brackets\n\n"

            "Every opening bracket should have a matching "
            "closing bracket."
        )

    # =====================================================
    # STRING ERROR
    # =====================================================

    if (
        "unterminated string" in text
        or "unterminated" in text
    ):

        return (
            "### 🔴 Unclosed String\n\n"

            "A string was started with a quotation mark "
            "but was not properly closed.\n\n"

            "**Wrong:**\n\n"

            "```python\n"
            "print(\"Hello)\n"
            "```\n\n"

            "**Correct:**\n\n"

            "```python\n"
            "print(\"Hello\")\n"
            "```"
        )

    # =====================================================
    # GCC
    # =====================================================

    if "gcc is not installed" in text:

        return (
            "### 🔴 GCC Compiler Not Found\n\n"

            "GCC is required to compile C programs.\n\n"

            "**Solution:**\n"
            "Install GCC and make sure `gcc` is available "
            "in your system PATH."
        )

    # =====================================================
    # G++
    # =====================================================

    if "g++ is not installed" in text:

        return (
            "### 🔴 G++ Compiler Not Found\n\n"

            "G++ is required to compile C++ programs.\n\n"

            "**Solution:**\n"
            "Install a C++ compiler and make sure `g++` "
            "is available in your system PATH."
        )

    # =====================================================
    # JAVA JDK
    # =====================================================

    if "java jdk is not installed" in text:

        return (
            "### 🔴 Java JDK Not Found\n\n"

            "Java programs require the Java Development Kit.\n\n"

            "Make sure both `java` and `javac` are installed "
            "and available in your system PATH."
        )

    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        f"### 🔴 {language} Program Error\n\n"

        "The program could not be executed successfully.\n\n"

        "**What to check:**\n"
        "1. Look at the error message above.\n"
        "2. Check the reported line number.\n"
        "3. Check the line immediately before it.\n"
        "4. Check brackets, variables and syntax.\n\n"

        "The exact solution depends on the error reported "
        "by the compiler or interpreter."
    )


# =========================================================
# ALGORITHM GENERATOR
# =========================================================

def make_algorithm(lines):

    steps = []

    for line in lines:

        kind = line_type(line)

        if kind == "condition":

            steps.append(
                "Check the condition: " + line
            )

        elif kind == "loop":

            steps.append(
                "Repeat according to the loop: " + line
            )

        elif kind == "input":

            steps.append(
                "Take input: " + line
            )

        elif kind == "output":

            steps.append(
                "Display output: " + line
            )

        elif kind == "assignment":

            steps.append(
                "Assign or update a value: " + line
            )

        elif kind == "function":

            steps.append(
                "Define or use a function: " + line
            )

        else:

            steps.append(
                "Execute: " + line
            )

    return steps


# =========================================================
# STEP EXPLANATION
# =========================================================

def explain_step(line, number):

    kind = line_type(line)

    if kind == "input":

        return (
            f"The program receives input from the user "
            f"using `{line}`."
        )

    if kind == "output":

        return (
            f"The program displays information using `{line}`."
        )

    if kind == "condition":

        return (
            f"The program evaluates the condition `{line}` "
            f"and selects the appropriate path."
        )

    if kind == "loop":

        return (
            f"The program starts or continues a loop using "
            f"`{line}`."
        )

    if kind == "assignment":

        return (
            f"A variable is assigned or updated using `{line}`."
        )

    if kind == "function":

        return (
            f"The program defines or uses a function with "
            f"`{line}`."
        )

    return (
        f"The program executes `{line}`."
    )


# =========================================================
# CODE EDITOR
# =========================================================

left, right = st.columns(
    [1.5, 1]
)


# =========================================================
# LEFT
# =========================================================

with left:

    st.markdown(
        '<div class="box">',
        unsafe_allow_html=True
    )

    st.subheader(
        "1️⃣ Select Programming Language"
    )

    languages = [
        "Python",
        "C",
        "C++",
        "Java"
    ]

    language = st.selectbox(
        "Language",
        languages,
        index=languages.index(
            st.session_state.language
        )
    )

    st.session_state.language = language

    st.subheader(
        "2️⃣ Enter Your Code"
    )

    code = st.text_area(
        "Code Editor",
        value=st.session_state.code,
        height=300,
        placeholder="Write or paste your code here..."
    )

    st.session_state.code = code

    run = st.button(
        "▶ RUN CODE",
        type="primary",
        use_container_width=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# RIGHT - OUTPUT
# =========================================================

with right:

    st.markdown(
        '<div class="box">',
        unsafe_allow_html=True
    )

    st.subheader(
        "📤 Program Output"
    )

    if run:

        st.session_state.output = ""
        st.session_state.error = ""
        st.session_state.view = ""

        if not code.strip():

            st.session_state.error = (
                "Please enter your code first."
            )

        else:

            with st.spinner(
                "Running your program..."
            ):

                output, error = run_program(
                    language,
                    code
                )

            st.session_state.output = output
            st.session_state.error = error

    if st.session_state.error:

        st.error(
            "Program Error"
        )

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
# VISUALIZATION BUTTONS
# =========================================================

st.subheader(
    "3️⃣ Choose Visualization Method"
)

c1, c2, c3 = st.columns(3)

with c1:

    if st.button(
        "🔄 VIEW FLOWCHART",
        use_container_width=True
    ):

        st.session_state.view = "flowchart"

with c2:

    if st.button(
        "📝 VIEW ALGORITHM",
        use_container_width=True
    ):

        st.session_state.view = "algorithm"

with c3:

    if st.button(
        "▶️ VIEW STEP-BY-STEP",
        use_container_width=True
    ):

        st.session_state.view = "steps"


# =========================================================
# DIVIDER
# =========================================================

st.divider()


# =========================================================
# LAB ASSISTANT
# =========================================================

if st.session_state.error:

    st.header(
        "🧪 Lab Assistant"
    )

    st.markdown(
        """
        <div class="assistant">
        <b>💡 What went wrong?</b>
        <br><br>
        The Smart Lab Assistant analyzed the error and
        generated an explanation below.
        </div>
        """,
        unsafe_allow_html=True
    )

    explanation = explain_error(
        language,
        st.session_state.error
    )

    st.markdown(
        explanation
    )

    st.subheader(
        "🔍 Actual Error"
    )

    st.code(
        st.session_state.error,
        language="text"
    )

    st.subheader(
        "✅ Lab Checks"
    )

    checks = {

        "Python": [
            "Check variable names and spelling",
            "Check (), [] and {}",
            "Check quotes and colons",
            "Check indentation",
            "Check variables are defined before use"
        ],

        "C": [
            "Check variable declarations",
            "Check semicolon ;",
            "Check (), [] and {}",
            "Check #include statements",
            "Check GCC installation"
        ],

        "C++": [
            "Check variable declarations",
            "Check semicolon ;",
            "Check (), [] and {}",
            "Check #include statements",
            "Check G++ installation"
        ],

        "Java": [
            "Check variable declarations",
            "Check (), [] and {}",
            "Check semicolon ;",
            "Use class Main",
            "Check Java JDK installation"
        ]
    }

    for item in checks[language]:

        st.write(
            "• " + item
        )


# =========================================================
# VISUALIZATION
# =========================================================

if not code.strip():

    st.info(
        "Enter code above and choose a visualization method."
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
            '<div class="startend">🟢 START</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="arrow">↓</div>',
            unsafe_allow_html=True
        )

        for index, line in enumerate(lines):

            kind = line_type(line)

            safe_line = html.escape(line)

            if kind == "condition":

                st.markdown(
                    f"""
                    <div class="decision">
                    🔷 DECISION
                    <br><br>
                    <b>{safe_line}</b>
                    <br><br>
                    <span style="color:#16a34a;">
                    YES / TRUE
                    </span>
                    &nbsp;&nbsp;&nbsp;
                    <span style="color:#dc2626;">
                    NO / FALSE
                    </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif kind == "loop":

                st.markdown(
                    f"""
                    <div class="decision">
                    🔁 LOOP
                    <br><br>
                    <b>{safe_line}</b>
                    <br><br>
                    Repeat while the loop condition is satisfied.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif kind == "input":

                st.markdown(
                    f"""
                    <div class="flow">
                    📥 INPUT
                    <br><br>
                    <b>{safe_line}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif kind == "output":

                st.markdown(
                    f"""
                    <div class="flow">
                    📤 OUTPUT
                    <br><br>
                    <b>{safe_line}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif kind == "assignment":

                st.markdown(
                    f"""
                    <div class="flow">
                    📦 PROCESS / ASSIGNMENT
                    <br><br>
                    <b>{safe_line}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif kind == "function":

                st.markdown(
                    f"""
                    <div class="flow">
                    ⚙️ FUNCTION
                    <br><br>
                    <b>{safe_line}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="flow">
                    ⚙️ PROCESS
                    <br><br>
                    <b>{safe_line}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if index < len(lines) - 1:

                st.markdown(
                    '<div class="arrow">↓</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            '<div class="arrow">↓</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="startend">🔴 END</div>',
            unsafe_allow_html=True
        )


    # =====================================================
    # ALGORITHM
    # =====================================================

    elif st.session_state.view == "algorithm":

        st.header(
            "📝 Algorithm"
        )

        st.caption(
            f"Algorithm generated from {language} code"
        )

        algorithm = make_algorithm(lines)

        st.markdown(
            '<div class="box">',
            unsafe_allow_html=True
        )

        st.markdown(
            "### Algorithm Steps"
        )

        st.write(
            "1. Start the program."
        )

        for index, step in enumerate(
            algorithm,
            start=2
        ):

            st.write(
                f"{index}. {step}"
            )

        st.write(
            f"{len(algorithm) + 2}. End the program."
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # =====================================================
    # STEP BY STEP
    # =====================================================

    elif st.session_state.view == "steps":

        st.header(
            "▶️ Step-by-Step Code Execution"
        )

        st.caption(
            f"Understanding each line of the {language} program"
        )

        st.markdown(
            """
            <div class="success-box">
            <b>🟢 Step 1 — Start</b>
            <br><br>
            The program begins execution.
            </div>
            """,
            unsafe_allow_html=True
        )

        for index, line in enumerate(
            lines,
            start=2
        ):

            explanation = explain_step(
                line,
                index
            )

            kind = line_type(line)

            if kind == "condition":

                icon = "🔷"

            elif kind == "loop":

                icon = "🔁"

            elif kind == "input":

                icon = "📥"

            elif kind == "output":

                icon = "📤"

            elif kind == "assignment":

                icon = "📦"

            elif kind == "function":

                icon = "⚙️"

            else:

                icon = "▶️"

            st.markdown(
                f"""
                <div class="step">

                <div class="step-number">
                {icon} Step {index}
                </div>

                <br>

                <code>{html.escape(line)}</code>

                <br><br>

                {html.escape(explanation)}

                </div>
                """,
                unsafe_allow_html=True
            )

        end_step = len(lines) + 2

        st.markdown(
            f"""
            <div class="success-box">
            <b>🔴 Step {end_step} — End</b>
            <br><br>
            The program reaches the end of execution.
            </div>
            """,
            unsafe_allow_html=True
        )


    # =====================================================
    # DEFAULT
    # =====================================================

    else:

        st.info(
            "Choose Flowchart, Algorithm, or "
            "Step-by-Step to visualize your code."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#64748b;padding:10px;">

    🧠 <b>Smart Code Visualizer</b>

    <br>

    Learn • Run • Visualize • Understand

    </div>
    """,
    unsafe_allow_html=True
)
