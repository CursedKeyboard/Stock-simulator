import dearpygui.core as gg
from dearpygui.simple import *
from new_user import create_database, get_user_data
import os

gg.show_logger()
gg.set_log_level(gg.mvTRACE)
gg.log("trace message")
gg.log_debug("debug message")
gg.log_info("info message")
gg.log_warning("warning message")
gg.log_error("error message")


def create_new_user_gui():
    with window("Main"):
        gg.add_input_text(
            name="##user_name",
            hint="User name",
            tip="Your username",
            parent="Main"
            )
        gg.add_input_int(
            name="##balance_input",
            default_value=500,
            tip="Your starting balance",
            parent="Main"
            )

        def create_new_user_data(sender, data) -> None:
            initial_data = {
            "User Name": gg.get_value("##user_name"),
            "Start Balance": gg.get_value("##balance_input")
            }

            if not initial_data["User Name"].isalpha():
                gg.add_label_text("Error", color=(255, 0, 0), before="##balance_input",label="Username must be alphabetical")
                gg.log_error("User-name must be only alphabets")
                return
            elif initial_data["User Name"] + ".db" in os.listdir():
                gg.add_label_text("Error", color=(255, 0, 0), before="##balance_input",label="Username already exists!")
                gg.log_error("User-name must be unique")
                return

            if initial_data["Start Balance"] <= 0:
                gg.add_label_text("Error_start_balance", color=(255, 0, 0, 1), before="Proceed",label="Balance must be greater than 0$")
                gg.log_error("Balance must be greater than 0$!")
                return
            
            create_database(initial_data["User Name"] + ".db", initial_data["Start Balance"])
            gg.delete_item("Main")
            initial_screen()
        
        gg.add_button("Proceed", callback=create_new_user_data)

def initial_screen():
    with window("Main"):

        def change_to_choosing_user(sender, data):
            gg.delete_item("Main")
            choose_user_screen()

        gg.add_button("Load", callback=change_to_choosing_user)

        def change_to_new_user(sender, data):
            gg.delete_item("Main")
            create_new_user_gui()

        gg.add_button("New", callback=change_to_new_user)

def choose_user_screen():
    with window("Choose User",width=600):

        # headers = ("USERNAME", "STARTING BALANCE", "CURRENT BALANCE", "DATE CREATED", "")
        # gg.add_table("files", headers=headers)
        gg.add_separator()
        with managed_columns("row", 5):
            gg.add_text("USERNAME")
            gg.add_text("STARTING BALANCE")
            gg.add_text("CURRENT BALANCE")
            gg.add_text("DATE CREATED")
            gg.add_text("")
        gg.add_separator()

        for file in os.listdir():
            count = 1
            if(file[-3:]) == ".db":
                user_name = file[:-3]
                initial_balance, current_balance, date_created = get_user_data(file)
                with managed_columns(f"row{count}", 5):
                    gg.add_text(f"{user_name}")
                    gg.add_text(f"{initial_balance}")
                    gg.add_text(f"{current_balance}")
                    gg.add_text(f"{date_created}")
                    gg.add_button(f"load {user_name}")
                gg.add_separator()
                count += 1

if __name__ == "__main__":
    initial_screen()

    gg.start_dearpygui()
