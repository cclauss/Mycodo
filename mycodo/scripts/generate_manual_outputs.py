# -*- coding: utf-8 -*-
"""Generate markdown file of Output information to be inserted into the manual"""

import sys

import os

sys.path.append(os.path.abspath(os.path.join(__file__, "../../..")))

import re
from collections import OrderedDict

from mycodo.config import INSTALL_DIRECTORY
from mycodo.utils.outputs import parse_output_information

save_path = os.path.join(INSTALL_DIRECTORY, "docs/Supported-Outputs.md")

outputs_info = OrderedDict()
mycodo_info = OrderedDict()


def repeat_to_length(s, wanted):
    return (s * (wanted//len(s) + 1))[:wanted]


if __name__ == "__main__":
    for output_id, output_data in parse_output_information(exclude_custom=True).items():
        name_str = ""
        if 'output_name' in output_data and output_data['output_name']:
            name_str += "{}".format(output_data['output_name'])
        if 'output_manufacturer' in output_data and output_data['output_manufacturer']:
            name_str += ": {}".format(output_data['output_manufacturer'])
        if 'measurements_name' in output_data and output_data['measurements_name']:
            name_str += ": {}".format(output_data['measurements_name'])
        if 'output_library' in output_data and output_data['output_library']:
            name_str += ": {}".format(output_data['output_library'])

        if ('output_manufacturer' in output_data and
                output_data['output_manufacturer'] in ['Linux', 'Mycodo', 'Raspberry Pi', 'System']):

            if name_str in mycodo_info and 'dependencies_module' in mycodo_info[name_str]:
                # Multiple sets of dependencies, append library
                mycodo_info[name_str]['dependencies_module'].append(output_data['dependencies_module'])
            else:
                # Only one set of dependencies
                mycodo_info[name_str] = output_data
                if 'dependencies_module' in output_data:
                    mycodo_info[name_str]['dependencies_module'] = [output_data['dependencies_module']]  # turn into list
        else:
            if name_str in outputs_info and 'dependencies_module' in outputs_info[name_str]:
                # Multiple sets of dependencies, append library
                outputs_info[name_str]['dependencies_module'].append(output_data['dependencies_module'])
            else:
                # Only one set of dependencies
                outputs_info[name_str] = output_data
                if 'dependencies_module' in output_data:
                    outputs_info[name_str]['dependencies_module'] = [output_data['dependencies_module']]  # turn into list

    mycodo_info = dict(OrderedDict(sorted(mycodo_info.items(), key = lambda t: t[0])))
    outputs_info = dict(OrderedDict(sorted(outputs_info.items(), key = lambda t: t[0])))

    list_outputs = [
        (mycodo_info, "Built-In Outputs (System)"),
        (outputs_info, "Built-In Outputs (Devices)")
    ]

    with open(save_path, 'w') as out_file:
        out_file.write("Supported Outputs are listed below.\n\n")
        for each_list in list_outputs:
            out_file.write("## {}\n\n".format(each_list[1]))

            for each_id, each_data in each_list[0].items():
                if 'output_name' in each_data and each_data['output_name']:
                    out_file.write("### {}\n\n".format(each_data['output_name']))
                else:
                    out_file.write("### {}\n\n".format(each_id))

                if 'output_manufacturer' in each_data and each_data['output_manufacturer']:
                    out_file.write("- Manufacturer: {}\n".format(each_data['output_manufacturer']))

                if 'measurements_name' in each_data and each_data['measurements_name']:
                    out_file.write("- Measurements: {}\n".format(each_data['measurements_name']))

                if 'interfaces' in each_data and each_data['interfaces']:
                    list_interfaces = []
                    for each_type in each_data['interfaces']:
                        if each_type == 'I2C':
                            list_interfaces.append("I<sup>2</sup>C")
                        elif each_type == 'MYCODO':
                            list_interfaces.append("Mycodo")
                        elif each_type == '1WIRE':
                            list_interfaces.append("1-Wire")
                        elif each_type == 'HTTP':
                            list_interfaces.append("HTTP")
                        elif each_type == 'FTDI':
                            list_interfaces.append("FTDI")
                        elif each_type == 'UART':
                            list_interfaces.append("UART")
                        elif each_type == 'GPIO':
                            list_interfaces.append("GPIO")
                        elif each_type == 'PYTHON':
                            list_interfaces.append("Python")
                        elif each_type == 'SHELL':
                            list_interfaces.append("Shell")
                        else:
                            list_interfaces.append(each_type)
                    out_file.write("- Interfaces: {}\n".format(", ".join(list_interfaces)))

                if 'output_types' in each_data and each_data['output_types']:
                    list_output_types = []
                    for each_type in each_data['output_types']:
                        if each_type == 'on_off':
                            list_output_types.append("On/Off")
                        elif each_type == 'volume':
                            list_output_types.append("Volume")
                        elif each_type == 'pwm':
                            list_output_types.append("PWM")
                        elif each_type == 'value':
                            list_output_types.append("Value")
                    out_file.write("- Output Types: {}\n".format(", ".join(list_output_types)))

                if 'output_library' in each_data and each_data['output_library']:
                    out_file.write("- Libraries: {}\n".format(each_data['output_library']))

                if 'dependencies_module' in each_data and each_data['dependencies_module']:
                    out_file.write("- Dependencies: ")
                    for i, each_dep_set in enumerate(each_data['dependencies_module']):
                        if len(each_data['dependencies_module']) > 1:
                            out_file.write("Output Variant {}: ".format(i + 1))
                        for i_d, each_dep in enumerate(each_dep_set):
                            if each_dep[0] == "apt":
                                out_file.write("[{0}](https://packages.debian.org/buster/{0})".format(each_dep[2]))
                            elif each_dep[0] == "pip-pypi":
                                if 'git+' in each_dep[2]:
                                    url = re.search('git\+(.*).git', each_dep[2])
                                    out_file.write("[{name}]({url})".format(name=each_dep[1], url=url.group(1)))
                                elif "==" in each_dep[2]:
                                    out_file.write("[{0}](https://pypi.org/project/{0})".format(each_dep[2].split("==")[0]))
                                else:
                                    out_file.write("[{0}](https://pypi.org/project/{0})".format(each_dep[2]))
                            elif each_dep[0] == "pip-git":
                                url = re.search('git://(.*).git', each_dep[2])
                                out_file.write("[{name}](https://{url})".format(name=each_dep[1], url=url.group(1)))
                            else:
                                out_file.write(each_dep[2])

                            if i_d + 1 < len(each_dep_set):
                                out_file.write(", ")

                        if i + 1 < len(each_data['dependencies_module']):
                            out_file.write("; ")
                        else:
                            out_file.write("\n")

                if 'url_manufacturer' in each_data and each_data['url_manufacturer']:
                    out_file.write("- Manufacturer URL")
                    if len(each_data['url_manufacturer']) == 1:
                        out_file.write(": ")
                    else:
                        out_file.write("s: ")
                    for i, each_url in enumerate(each_data['url_manufacturer']):
                        if len(each_data['url_manufacturer']) == 1:
                            out_file.write("[Link]({})".format(each_url))
                        else:
                            out_file.write("[Link {num}]({url})".format(num=i + 1, url=each_url))
                        if i + 1 < len(each_data['url_manufacturer']):
                            out_file.write(", ")
                        else:
                            out_file.write("\n")

                if 'url_datasheet' in each_data and each_data['url_datasheet']:
                    out_file.write("- Datasheet URL")
                    if len(each_data['url_datasheet']) == 1:
                        out_file.write(": ")
                    else:
                        out_file.write("s: ")
                    for i, each_url in enumerate(each_data['url_datasheet']):
                        if len(each_data['url_datasheet']) == 1:
                            out_file.write("[Link]({})".format(each_url))
                        else:
                            out_file.write("[Link {num}]({url})".format(num=i + 1, url=each_url))
                        if i + 1 < len(each_data['url_datasheet']):
                            out_file.write(", ")
                        else:
                            out_file.write("\n")

                if 'url_product_purchase' in each_data and each_data['url_product_purchase']:
                    out_file.write("- Product URL")
                    if len(each_data['url_product_purchase']) == 1:
                        out_file.write(": ")
                    else:
                        out_file.write("s: ")
                    for i, each_url in enumerate(each_data['url_product_purchase']):
                        if len(each_data['url_product_purchase']) == 1:
                            out_file.write("[Link]({})".format(each_url))
                        else:
                            out_file.write("[Link {num}]({url})".format(num=i + 1, url=each_url))
                        if i + 1 < len(each_data['url_product_purchase']):
                            out_file.write(", ")
                        else:
                            out_file.write("\n")

                if 'url_additional' in each_data and each_data['url_additional']:
                    if len(each_data['url_additional']) == 1:
                        out_file.write("- Additional URL: ")
                    else:
                        out_file.write("- Additional URL(s): ")
                    for i, each_url in enumerate(each_data['url_additional']):
                        if len(each_data['url_additional']) == 1:
                            out_file.write("[Link]({})".format(each_url))
                        else:
                            out_file.write("[Link {num}]({url})".format(num=i + 1, url=each_url))
                        if i + 1 < len(each_data['url_additional']):
                            out_file.write(", ")
                        else:
                            out_file.write("\n")

                if 'message' in each_data and each_data['message']:
                    out_file.write("\n{}\n".format(each_data['message']))

                out_file.write("\n")
