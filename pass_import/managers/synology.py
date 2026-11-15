# -*- encoding: utf-8 -*-
# pass import - Passwords importer swiss army knife
# Copyright (C) 2024 SAY-5 <say.apm35@gmail.com>.
# Copyright (C) 2026 Ahmad Othman <ahmad.ali.othman@outlook.com>.
#

from pass_import.errors import FormatError
import json
from typing import TypedDict
from pass_import.core import register_managers
from pass_import.formats.csv import CSV


class CustomAutofillField(TypedDict):
    Type: str
    AutofillWeb_Title: str
    AutofillWeb_Type: str
    AutofillWeb: str
    AutofillWeb_Selector: str


class CustomTextField(TypedDict):
    Type: str
    Text_Title: str
    Text: str


class SynologyC2CSV(CSV):
    """Importer for Synology C2 Password in CSV format."""
    name = 'synology'
    url = 'https://c2.synology.com/en-global/password/overview'
    hexport = 'Profile > Export > Download'
    himport = 'pass import synology file.csv'
    encoding = 'utf-8-sig'
    keys = {
        'title': 'Display_Name',
        'login': 'Login_Username',
        'password': 'Login_Password',
        'url': 'Login_URLs',
        'otpauth': 'Login_TOTP',
        'comments': 'Notes'
    }

    def parse(self):
        """Parse C2 Password CSV file, handling custom fields in Others column."""
        super().parse()
        for entry in self.data:
            entry.pop("Login_URL_Match_Rules", None)
            entry.pop("Tag", None)
            entry.pop("Tag_Color", None)
            entry.pop("Favorite", None)

            raw = entry.pop("Others", "")
            if raw and raw.strip():
                try:
                    others = json.loads(raw)
                    if "Custom" in others:
                        custom = others.get("Custom")
                        if isinstance(custom, list):
                            for item in custom:
                                if item["Type"] == "Text":
                                    field: CustomTextField = item
                                    entry[field["Text_Title"].title()] = field["Text"]
                                elif item["Type"] == "AutofillWeb":
                                    field: CustomAutofillField = item
                                    entry[field["AutofillWeb_Title"].title()] = field["AutofillWeb"]

                except json.JSONDecodeError as e:
                    raise FormatError(f"Invalid JSON in 'Others' column: {e}")


register_managers(SynologyC2CSV)
