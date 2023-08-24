from dataclasses import dataclass
import os
import xml.etree.ElementTree as ET
import subprocess
import datetime


def _getDxdiag_xml() -> ET.Element:
    f_name = "dxdiag.xml"
    if datetime.datetime.today().date() == datetime.datetime.fromtimestamp(os.path.getctime(filename=f_name)).date():
        return ET.parse(f_name).getroot()
    sprocess = subprocess.Popen(["dxdiag", "/x", f_name], stdout=subprocess.PIPE, shell=True)
    _, stderrdata = sprocess.communicate()
    if stderrdata:
        raise Exception(stderrdata)

    return ET.parse(f_name).getroot()


@dataclass
class SystemInfo:
    machine_name: str
    machine_id: str
    operating_system: str
    system_manufacturer: str
    system_model: str
    bios: str
    firmware_type: str
    processor: str


def get_sys_info(xml_root) -> SystemInfo:
    sys_info_xml = xml_root.find("SystemInformation")
    sys_info_tuple = (
        sys_info_xml.find("MachineName").text,
        sys_info_xml.find("MachineId").text,
        sys_info_xml.find("OperatingSystem").text.split("(")[0].strip(),  # remove build number # type: ignore
        sys_info_xml.find("SystemManufacturer").text,
        sys_info_xml.find("SystemModel").text,
        sys_info_xml.find("BIOS").text,
        sys_info_xml.find("FirmwareType").text,
        sys_info_xml.find("Processor").text,
    )
    return SystemInfo(*sys_info_tuple)  # type: ignore


xml_root = _getDxdiag_xml()
# for child in xml_root:
#     if child.tag == "SystemInformation":
#         for sys_info in child.iter():
#             match sys_info.tag:
#                 case "MachineName":
#                     machine_name = sys_info.text
#                 case "MachineId":
#                     machine_id = sys_info.text
#                 case "OperatingSystem":
#                     operating_system = sys_info.text
#                     operating_system = operating_system[: operating_system.find("(")].strip()  # remove build number # type: ignore
#                 case "SystemManufacturer":
#                     system_manufacturer = sys_info.text
#                 case "SystemModel":
#                     system_model = sys_info.text
#                 case "BIOS":
#                     bios = sys_info.text
#                 case "FirmwareType":
#                     firmware_type = sys_info.text
#                 case "Processor":
#                     processor = sys_info.text
#                 case _:
#                     pass
#         break


print(get_sys_info(xml_root))
