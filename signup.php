<?php
?>

<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sign Up - Astro</title>

        <style>
            body {
                background: #000000;
                color: #EBD7FF;
                font-family: Verdana, sans-serif;
            }
            .container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                flex-direction: column;
            }
            svg {
                margin-bottom: 20px;
            }
            form {
                display: flex;
                flex-direction: column;
                width: 50%;
                align-items: center;
            }
            input {
                width: 50%;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                font-family: inherit;
                background-color: #EBD7FF;
            }
            input::placeholder {
                color: #000000;
            }
            .first-last-name {
                display: flex;
                justify-content: space-between;
                width: 50%;
            }
            .first-last-name input {
                width: calc(50% - 2px);
            }
            button {
                width: 50%;
                background-color: #972FFF;
                color: #EBD7FF;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
        </style>
    </head>

    <body>
        <div class = "container">
            <svg xmlns="http://www.w3.org/2000/svg" width = "72" height = "72" viewBox = "0 0 24 24" fill = "none"
                 stroke = "currentColor" stroke-width = "2" stroke-linecap = "round" stroke-linejoin = "round"
                 class = "icon icon-tabler icons-tabler-outline icon-tabler-moon-stars">
                <path stroke = "none" d = "M0 0h24v24H0z" fill = "none"/>
                <path d = "M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z"/>
                <path d = "M17 4a2 2 0 0 0 2 2a2 2 0 0 0 -2 2a2 2 0 0 0 -2 -2a2 2 0 0 0 2 -2"/>
                <path d="M19 11h2m-1 -1v2" /></svg>
            <form method = "post">
                <div class = "first-last-name">
                    <input type = "text" name = "firstname" placeholder = "First Name" required>
                    <input type = "text" name = "lastname" placeholder = "Last Name" required>
                </div>
                <input type = "email" name = "email" placeholder = "Email" required>
                <input type = "text" name = "username" placeholder = "Username" required>
                <input type = "password" name = "password" placeholder = "Password" required>
                <input type = "password" name = "confirm-password" placeholder = "Confirm Password" required>
                <button type = "submit">Sign Up</button>
            </form>
        </div>
    </body>
</html>