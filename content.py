def Content():
    APP_CONTENT = {
        "Home":[["Welcome", "/welcome/", "Welcome to my awesome app!"],
               ["Background", "/background/", "Learn more about the app here!"],
               ["Messages", "/messages/", "Your user messages are waiting..."],],
        "Profile":[["User Profile", "/profile/", "Edit your profile here!"],
                  ["Settings", "/settings/", "App Settings"],
                  ["Terms of Service", "/tos", "The legal stuff"],],
        "Messages":[["Messages", "/messages/", "Your user messages are waiting..."],
                   ["Alerts", "/alerts/", "Urgent Alerts"],],
        "Contact" :[["Contact", "/contact/", "Contact us for support"],],
    }
    return APP_CONTENT