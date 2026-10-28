
import ast
import re
import subprocess
import sys
import streamlit as st

st.set_page_config(
    page_title="CodeFix AI",
    page_icon="🐞",
    layout="wide"
)

st.title("🐞 CodeFix AI")
st.subheader("Beginner Code Error Detection and Explanation System")
st.write(
    "Enter your Python code to detect errors, understand them, "
    "view possible corrections, and see program output."
)


def check_code(code):
    """Check Python code for syntax errors."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as error:
        return error


def suggest_correction(code, error):
    """Suggest a few common syntax corrections."""
    lines = code.splitlines()

    if error.lineno and 1 <= error.lineno <= len(lines):
        line = lines[error.lineno - 1]
        stripped = line.strip()

        # Add a missing colon to common statements
        keywords = (
            "if ", "elif ", "else", "for ", "while ",
            "def ", "class ", "try", "except", "finally",
            "with "
        )

        if (
            stripped.startswith(keywords)
            and not stripped.endswith(":")
            and not stripped.endswith("\\")
        ):
            lines[error.lineno - 1] = line.rstrip() + ":"
            return "\n".join(lines)

        # Try adding a missing closing parenthesis
        if error.msg and "was never closed" in error.msg:
            if code.count("(") > code.count(")"):
                return code + ")"

        if error.msg and "unexpected EOF" in error.msg:
            if code.count("(") > code.count(")"):
                return code + ")"

    return None


def explain_error(error):
    """Explain common errors in simple English."""
    message = error.msg.lower()

    if "expected ':'" in message:
        return (
            "A colon (:) is missing at the end of a statement "
            "such as if, for, while, or def."
        )

    if "was never closed" in message:
        return (
            "An opening bracket, parenthesis, or quote may not "
            "have been closed correctly."
        )

    if "unexpected indent" in message:
        return (
            "There is an unnecessary indentation. Check the spaces "
            "at the beginning of the line."
        )

    if "invalid syntax" in message:
        return (
            "Python could not understand this statement. Check "
            "spelling, brackets, quotes, colons, and operators."
        )

    return (
        "Python found a syntax problem. Review the indicated line "
        "and check the spelling and punctuation."
    )


example = '''def check_number(n):
    if n > 0:
        print("Positive")
    else:
        print("Not positive")

check_number(10)'''

code = st.text_area(
    "✍️ Enter your Python code",
    value=example,
    height=250,
    placeholder='Example: print("Hello, World!")'
)

col1, col2 = st.columns(2)

with col1:
    check_button = st.button(
        "🔍 Detect Errors",
        use_container_width=True
    )

with col2:
    run_button = st.button(
        "▶️ Run Code & Show Output",
        use_container_width=True
    )

if check_button or run_button:
    if not code.strip():
        st.warning("Please enter some Python code first.")

    else:
        error = check_code(code)

        if error:
            st.error("❌ Syntax Error Detected")

            st.write(f"**Error:** {error.msg}")
            st.write(f"**Line number:** {error.lineno}")
            st.info(explain_error(error))

            corrected_code = suggest_correction(code, error)

            if corrected_code and corrected_code != code:
                st.subheader("💡 Suggested Correction")
                st.code(corrected_code, language="python")

                st.download_button(
                    "⬇️ Download Suggested Code",
                    data=corrected_code,
                    file_name="corrected_code.py",
                    mime="text/x-python"
                )
            else:
                st.warning(
                    "No automatic correction is available for this "
                    "error. Please check the code manually."
                )

            if run_button:
                st.warning(
                    "The program was not executed because it contains "
                    "a syntax error."
                )

        else:
            st.success("✅ No syntax errors found!")

            if check_button:
                st.info(
                    "Your code passed the syntax check. "
                    "Click 'Run Code & Show Output' to see its output."
                )

            if run_button:
                st.subheader("🖥️ Output Console")

                try:
                    result = subprocess.run(
                        [sys.executable, "-I", "-c", code],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )

                    if result.stdout:
                        st.code(result.stdout, language="text")
                    else:
                        st.info("The program produced no printed output.")

                    if result.stderr:
                        st.error("⚠️ Runtime Error or Warning")
                        st.code(result.stderr, language="text")

                    if result.returncode != 0:
                        st.write(
                            f"Program exit code: {result.returncode}"
                        )
                    elif not result.stderr:
                        st.success("✅ Program finished.")

                except subprocess.TimeoutExpired:
                    st.error(
                        "⏱️ Execution stopped after 3 seconds. "
                        "Your code may contain an infinite loop."
                    )

                except Exception as error:
                    st.error(f"Could not run the code: {error}")

st.divider()
st.caption(
    "CodeFix AI | Educational Mini-Capstone Project | Python + Streamlit"
)
st.warning(
    "Local demo only: this app executes submitted Python code. "
    "Do not expose it to untrusted users or deploy it publicly "
    "without a properly isolated, restricted execution sandbox."
)

