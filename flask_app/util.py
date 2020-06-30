from flask import render_template

def redirect_page(title, message, redirect_url, redirect_delay=3):
    message = message.format(delay=redirect_delay)
    return render_template('redirect.html', title=title, message=message,
                           url=redirect_url, delay=redirect_delay)
