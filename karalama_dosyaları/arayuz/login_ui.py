from tkinter import BooleanVar, Checkbutton, LabelFrame, PhotoImage, Tk, Frame, Label, Entry, Button
from tkinter.ttk import Combobox
from enum import Enum, auto

LOGO_PATH = "./arayuz/moe_logo.png"


def localization(
    key_name: str,
) -> str:
    # TODO  localization
    return key_name


class LocalizationEnum(Enum):
    EN = "English"
    TR = "Türkçe"


class SelectibleModEnum(Enum):
    moe_gatherer = auto()
    # moe_raid = auto()
    # moe_camp = auto()
    # moe_arena = auto()


class PagesEnum(Enum):
    LOGIN = auto()
    MOD_SELECT = auto()
    MOE_GATHERER = auto()


class ModEnum(Enum):
    MOE_GATHERER = auto()
    # MOE_RAID = auto()
    # MOE_CAMP = auto()
    # MOE_ARENA = auto()


class UnExpectedPageError(Exception):
    pass


class MainGui:
    __slots__ = ["root", "page", "pageshow", "language", "interaction_variables"]

    def __init__(self, root, title, geometry):
        self.root = root
        self.root.title(title)
        self.root.geometry(geometry)
        self.pageshow = Login_Page(self, self.root)
        self.language = LocalizationEnum.EN
        self.interaction_variables = {}

    def change_page(self, page):
        self.page = page

        if self.page == PagesEnum.LOGIN:
            # del self.pageshow
            self.pageshow = Login_Page(self, self.root)

        elif self.page == PagesEnum.MOD_SELECT:
            # del self.pageshow
            self.pageshow = Mod_Select_Page(self, self.root)

        elif self.page == PagesEnum.MOE_GATHERER:
            # del self.pageshow
            self.pageshow = Moe_Gatherer_Page(self, self.root)

    def make_interaction_variables_ready(self) -> None:
        if isinstance(self.pageshow.name, ModEnum):
            self.interaction_variables = {
                "language": self.language,
                "mod_name": self.pageshow.name,
                "mod_settings": self.pageshow.get_settings(),  # type: ignore
            }
            print(self.interaction_variables)
            self.root.destroy()
            return
        raise UnExpectedPageError("Unexpected page")


class Login_Page:
    def __init__(self, parent, window):
        self.parent = parent
        self.name = PagesEnum.LOGIN

        # change size of window to 360x140
        self.parent.root.geometry("360x140")

        self.frame = Frame(window)
        self.frame.pack()

        # -- language selection --

        self.select_lang_lbl = Label(self.frame, text=localization("select_lang_lbl"))
        self.select_lang_lbl.grid(row=4, column=0)

        self.select_lang_combo = Combobox(self.frame, values=[localization(lang.name) for lang in LocalizationEnum], state="readonly")
        self.select_lang_combo.grid(row=4, column=1)

        # -- language selection --

        # -- login --

        self.welcm_lbl = Label(self.frame, text="welcome")
        self.welcm_lbl.grid(row=0, column=1)

        self.name_lbl = Label(self.frame, text="name:")
        self.name_lbl.grid(row=1, column=0)

        self.name_entry = Entry(self.frame)
        self.name_entry.grid(row=1, column=1)

        self.pass_lbl = Label(self.frame, text="password:")
        self.pass_lbl.grid(row=2, column=0)

        self.pass_entry = Entry(self.frame)
        self.pass_entry.grid(row=2, column=1)

        self.sbt = Button(self.frame, text=localization("login_btn"), command=self.clicked)
        self.sbt.grid(row=3, column=1)

        # -- login --

    def clicked(self):
        self.frame.destroy()
        self.parent.change_page(PagesEnum.MOD_SELECT)


class Mod_Select_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.name = PagesEnum.MOD_SELECT

        # change size of window to 200x100
        self.parent.root.geometry("200x100")

        self.main_frame = Frame(window)
        self.main_frame.pack()

        self.mod_select_lbl = Label(self.main_frame, text="mod_select_lbl")
        self.mod_select_lbl.grid(row=0, column=1)

        self.mod_selection_combo = Combobox(
            self.main_frame, state="readonly", values=[localization(module.name) for module in SelectibleModEnum]
        )
        self.mod_selection_combo.grid(row=1, column=1)

        self.mod_select_continue_btn = Button(self.main_frame, text=localization("mod_select_continue_btn"), command=self.clicked)
        self.mod_select_continue_btn.grid(row=2, column=1)

    def clicked(self):
        self.main_frame.destroy()
        # TODO: go to selected mod page
        self.parent.change_page(PagesEnum.MOE_GATHERER)


class Moe_Gatherer_Page:
    def __init__(self, parent, window) -> None:
        self.parent = parent
        self.name = ModEnum.MOE_GATHERER

        # change size of window to 580x380
        self.parent.root.geometry("580x380")

        self.main_frame = Frame(window, padx=10, pady=10)
        self.main_frame.pack()

        self.moe_logo_img = PhotoImage(file=LOGO_PATH, width=100, height=100)
        self.moe_logo_lbl = Label(
            self.main_frame,
            text="moe_logo_lbl",
            image=self.moe_logo_img,
        )
        self.moe_logo_lbl.grid(row=0, column=0)
        # -- march selection --

        self.march_selection_lbl = LabelFrame(
            self.main_frame, text=localization("march_selection_lbl"), height=100, width=100, padx=10, pady=10
        )
        self.march_selection_lbl.grid(row=0, column=1)

        self.march_selection_combo = Combobox(
            self.march_selection_lbl, state="readonly", values=[str(march_count) for march_count in range(1, 8)]
        )
        self.march_selection_combo.grid(row=0, column=0)

        # -- resource selection --
        self.resource_selection_lbl = LabelFrame(
            self.main_frame, text=localization("resource_selection_lbl"), height=100, width=100, padx=10, pady=10
        )
        self.resource_selection_lbl.grid(row=1, column=0)

        self.resorce_variables = {
            "gold": BooleanVar(),
            "food": BooleanVar(),
            "wood": BooleanVar(),
            "stone": BooleanVar(),
            "iron": BooleanVar(),
            "silver": BooleanVar(),
        }

        self.resource_selection_checkbuttons = {
            resource: Checkbutton(
                self.resource_selection_lbl,
                onvalue=True,
                offvalue=False,
                text=localization(resource),
                variable=self.resorce_variables[resource],
            )
            for resource in self.resorce_variables
        }
        for i, resource in enumerate(self.resource_selection_checkbuttons):
            self.resource_selection_checkbuttons[resource].grid(row=i, column=0)

        self.resource_select_all_btn = Button(
            self.resource_selection_lbl, text=localization("resource_select_all_btn"), command=self.resource_select_all_clicked
        )
        self.resource_select_all_btn.grid(row=len(self.resorce_variables), column=0)

        self.resource_select_none_btn = Button(
            self.resource_selection_lbl, text=localization("resource_select_none_btn"), command=self.resource_select_none_clicked
        )
        self.resource_select_none_btn.grid(row=len(self.resorce_variables) + 1, column=0)

        # -- resource selection --

        # -- lvl selection --

        self.lvl_selection_lbl = LabelFrame(
            self.main_frame, text=localization("lvl_selection_lbl"), height=100, width=100, padx=10, pady=10
        )
        self.lvl_selection_lbl.grid(sticky="E", row=1, column=1, padx=10, pady=10, ipadx=10, ipady=10)

        self.lvl_selection_variables = [BooleanVar() for _ in range(1, 13)]

        self.lvl_selection_checkbuttons = {
            i: Checkbutton(
                self.lvl_selection_lbl,
                onvalue=True,
                offvalue=False,
                text=str(i),
                variable=self.lvl_selection_variables[i - 1],
                font=("Verdana 10"),
            )
            for i in range(1, len(self.lvl_selection_variables) + 1)
        }

        for i in range(1, len(self.lvl_selection_checkbuttons) + 1):
            if i < 7:
                self.lvl_selection_checkbuttons[i].grid(row=i - 1, column=0)
            else:
                self.lvl_selection_checkbuttons[i].grid(row=i - 7, column=1)

        self.lvl_select_all_btn = Button(
            self.lvl_selection_lbl, text=localization("lvl_select_all_btn"), command=self.lvl_select_all_clicked
        )
        self.lvl_select_all_btn.grid(row=6, column=0)
        self.lvl_select_all_btn = Button(
            self.lvl_selection_lbl, text=localization("lvl_select_none_btn"), command=self.lvl_select_none_clicked
        )
        self.lvl_select_all_btn.grid(row=6, column=1)

        # -- lvl selection --

        # -- close gui btn --

        self.close_gui_btn = Button(self.main_frame, text=localization("close_gui_btn"), command=self.clicked)
        self.close_gui_btn.grid(row=1, column=2)

    def resource_select_all_clicked(self):
        for resource in self.resorce_variables:
            self.resource_selection_checkbuttons[resource].select()

    def resource_select_none_clicked(self):
        for resource in self.resorce_variables:
            self.resource_selection_checkbuttons[resource].deselect()

    def lvl_select_all_clicked(self):
        for lvl in self.lvl_selection_checkbuttons:
            self.lvl_selection_checkbuttons[lvl].select()

    def lvl_select_none_clicked(self):
        for lvl in self.lvl_selection_checkbuttons:
            self.lvl_selection_checkbuttons[lvl].deselect()

    def get_settings(self) -> dict:
        return {
            "march_count": str(self.march_selection_combo.get()),
            "resources": [resource for resource in self.resorce_variables if self.resorce_variables[resource].get()],
            "lvls": [
                lvl_num
                for lvl_num in range(1, len(self.lvl_selection_variables) + 1)
                if self.lvl_selection_variables[lvl_num - 1].get()
            ],
        }

    def clicked(self):
        self.parent.make_interaction_variables_ready()


# class Sign_Page:
#     def __init__(self, parent, window):
#         self.parent = parent

#         self.frame = Frame(window)
#         self.frame.pack()

#         self.welcm_lbl = Label(self.frame, text="welcome sign-up")
#         self.welcm_lbl.grid(row=0, column=1)

#         self.name_lbl = Label(self.frame, text="name:")
#         self.name_lbl.grid(row=1, column=0)

#         self.name_entry = Entry(self.frame)
#         self.name_entry.grid(row=1, column=1)

#         self.sbt = Button(self.frame, text="sign-up", command=self.clicked)
#         self.sbt.grid(row=2, column=1)

#     def clicked(self):
#         self.frame.destroy()
#         self.parent.changepage(PagesEnum.LOGIN)


# def print_window_size(tk_root: Tk):
#     print(tk_root.winfo_width(), tk_root.winfo_height())


def main():
    root = Tk()
    MainGui(root, "Rpg", "400x400")
    root.attributes("-alpha", 0.95)
    # call print_window_size function when window size changes
    # root.bind("<Configure>", lambda e: print_window_size(root))
    root.mainloop()


if __name__ == "__main__":
    main()
