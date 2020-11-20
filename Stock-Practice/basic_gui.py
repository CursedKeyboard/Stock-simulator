import dearpygui.core as gg
from dearpygui.simple import *

gg.show_logger()
gg.set_log_level(gg.mvTRACE)
gg.log("trace message")
gg.log_debug("debug message")
gg.log_info("info message")
gg.log_warning("warning message")
gg.log_error("error message")

def get_user_data(sender, data):
    initial_data = {
        "User Name": gg.get_value("##user_name"),
        "Start Balance": gg.get_value("##balance_input")
    }
    if not initial_data["User Name"].isalpha():
        gg.add_label_text("Error", color=(255, 0, 0), before="##balance_input",label="Username must be alphabetical")
        gg.log_error("User-name must be only alphabets")
    
    if initial_data["Start Balance"] < 500:
        gg.add_label_text("Error_start_balance", color=(255, 0, 0, 1), before="Proceed",label="Balance must be atleast 500$")
        gg.log_error("Balance must be greater than 500!")

    print(initial_data)

def create_new_user_gui():
    with window("Example Window"):
        gg.add_input_text(name="##user_name",hint="User name")
        gg.add_input_int(name="##balance_input",default_value=500)
        gg.add_button("Proceed", callback=get_user_data)

    gg.start_dearpygui(primary_window="Example Window")

if __name__ == "__main__":
    create_new_user_gui()
