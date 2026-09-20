
document.addEventListener("DOMContentLoaded", () => {


    /* =====================================================
       MOBILE NAVIGATION
    ====================================================== */

    const mobileMenuBtn =
        document.getElementById("mobileMenuBtn");

    const navLinks =
        document.getElementById("navLinks");


    if (mobileMenuBtn && navLinks) {

        mobileMenuBtn.addEventListener("click", () => {

            navLinks.classList.toggle("active");

            const isOpen =
                navLinks.classList.contains("active");

            mobileMenuBtn.setAttribute(
                "aria-label",
                isOpen ? "Close menu" : "Open menu"
            );

            mobileMenuBtn.textContent =
                isOpen ? "✕" : "☰";

        });


        /* Close mobile menu after clicking a link */

        navLinks.querySelectorAll("a").forEach((link) => {

            link.addEventListener("click", () => {

                navLinks.classList.remove("active");

                mobileMenuBtn.textContent = "☰";

                mobileMenuBtn.setAttribute(
                    "aria-label",
                    "Open menu"
                );

            });

        });

    }



    /* =====================================================
       PASSWORD SHOW / HIDE
    ====================================================== */

    document
        .querySelectorAll(".password-toggle")
        .forEach((button) => {

            button.addEventListener("click", () => {

                const targetId =
                    button.getAttribute("data-target");

                const input =
                    document.getElementById(targetId);


                if (!input) {
                    return;
                }


                if (input.type === "password") {

                    input.type = "text";

                    button.textContent = "🙈";

                    button.setAttribute(
                        "aria-label",
                        "Hide password"
                    );

                } else {

                    input.type = "password";

                    button.textContent = "👁";

                    button.setAttribute(
                        "aria-label",
                        "Show password"
                    );

                }

            });

        });



    /* =====================================================
       QUIZ
    ====================================================== */

    const quizForm =
        document.getElementById("quizForm");

    const answeredCount =
        document.getElementById("answeredCount");

    const progressBar =
        document.getElementById("quizProgressBar");


    if (quizForm) {


        /* Get unique question groups */

        const getQuestionGroups = () => {

            return [
                ...new Set(
                    [
                        ...quizForm.querySelectorAll(
                            'input[type="radio"]'
                        )
                    ].map(
                        (input) => input.name
                    )
                )
            ];

        };


        /* Update answered counter */

        const updateQuizProgress = () => {

            const groups =
                getQuestionGroups();


            let answered = 0;


            groups.forEach((name) => {

                const selected =
                    quizForm.querySelector(
                        `input[name="${name}"]:checked`
                    );


                if (selected) {
                    answered++;
                }

            });


            const total =
                groups.length;


            if (answeredCount) {

                answeredCount.textContent =
                    answered;

            }


            if (progressBar) {

                const percentage =
                    total > 0
                        ? (answered / total) * 100
                        : 0;


                progressBar.style.width =
                    `${percentage}%`;

            }

        };


        /* Listen for answer changes */

        quizForm.addEventListener(
            "change",
            updateQuizProgress
        );


        /* Validate before submitting */

        quizForm.addEventListener(
            "submit",
            (event) => {

                const groups =
                    getQuestionGroups();


                const unanswered =
                    groups.filter((name) => {

                        return !quizForm.querySelector(
                            `input[name="${name}"]:checked`
                        );

                    });


                if (unanswered.length > 0) {

                    event.preventDefault();


                    alert(
                        `Please answer all questions. ` +
                        `${unanswered.length} question(s) remaining.`
                    );


                    const firstUnanswered =
                        quizForm.querySelector(
                            `input[name="${unanswered[0]}"]`
                        );


                    if (firstUnanswered) {

                        const questionCard =
                            firstUnanswered.closest(
                                ".question-card"
                            );


                        if (questionCard) {

                            questionCard.scrollIntoView({
                                behavior: "smooth",
                                block: "center"
                            });

                        }

                    }


                    return;

                }


                /* Prevent double submission */

                const submitButton =
                    quizForm.querySelector(
                        "button[type='submit']"
                    );


                if (submitButton) {

                    submitButton.disabled = true;

                    submitButton.innerHTML =
                        "Submitting...";

                }

            }
        );


        updateQuizProgress();

    }



    /* =====================================================
       FLASH MESSAGE AUTO DISMISS
    ====================================================== */

    document
        .querySelectorAll(".flash")
        .forEach((flash) => {

            setTimeout(() => {

                flash.classList.add("hide");


                setTimeout(() => {

                    flash.remove();

                }, 400);

            }, 4500);

        });



    /* =====================================================
       FLASH MESSAGE CLOSE BUTTON
    ====================================================== */

    document
        .querySelectorAll(".flash-close")
        .forEach((button) => {

            button.addEventListener("click", () => {

                const flash =
                    button.closest(".flash");


                if (flash) {

                    flash.classList.add("hide");


                    setTimeout(() => {

                        flash.remove();

                    }, 400);

                }

            });

        });



    /* =====================================================
       CONFIRM PASSWORD VALIDATION
    ====================================================== */

    const registerForm =
        document.querySelector(
            'form[action*="register"]'
        );


    if (registerForm) {

        registerForm.addEventListener(
            "submit",
            (event) => {

                const password =
                    registerForm.querySelector(
                        'input[name="password"]'
                    );

                const confirmPassword =
                    registerForm.querySelector(
                        'input[name="confirm_password"]'
                    );


                if (
                    password &&
                    confirmPassword &&
                    password.value !== confirmPassword.value
                ) {

                    event.preventDefault();


                    alert(
                        "Passwords do not match."
                    );


                    confirmPassword.focus();

                }

            }
        );

    }



    /* =====================================================
       RESET PASSWORD VALIDATION
    ====================================================== */

    const forgotForm =
        document.querySelector(
            'form[action*="forgot-password"]'
        );


    if (forgotForm) {

        forgotForm.addEventListener(
            "submit",
            (event) => {

                const password =
                    forgotForm.querySelector(
                        'input[name="new_password"]'
                    );

                const confirmPassword =
                    forgotForm.querySelector(
                        'input[name="confirm_password"]'
                    );


                if (
                    password &&
                    confirmPassword &&
                    password.value !== confirmPassword.value
                ) {

                    event.preventDefault();


                    alert(
                        "Passwords do not match."
                    );


                    confirmPassword.focus();

                }

            }
        );

    }



    /* =====================================================
       CHANGE PASSWORD VALIDATION
    ====================================================== */

    const changePasswordForm =
        document.querySelector(
            'form[action*="change-password"]'
        );


    if (changePasswordForm) {

        changePasswordForm.addEventListener(
            "submit",
            (event) => {

                const password =
                    changePasswordForm.querySelector(
                        'input[name="new_password"]'
                    );

                const confirmPassword =
                    changePasswordForm.querySelector(
                        'input[name="confirm_password"]'
                    );


                if (
                    password &&
                    confirmPassword &&
                    password.value !== confirmPassword.value
                ) {

                    event.preventDefault();


                    alert(
                        "New passwords do not match."
                    );


                    confirmPassword.focus();

                }

            }
        );

    }



    /* =====================================================
       SMOOTH ANCHOR SCROLL
    ====================================================== */

    document
        .querySelectorAll('a[href^="#"]')
        .forEach((link) => {

            link.addEventListener("click", (event) => {

                const targetId =
                    link.getAttribute("href");


                if (
                    !targetId ||
                    targetId === "#"
                ) {
                    return;
                }


                const target =
                    document.querySelector(targetId);


                if (target) {

                    event.preventDefault();


                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }

            });

        });


});

