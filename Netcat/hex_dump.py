def format_hex_dump(raw_bytes, label):
    output_lines = []
    output_lines.append(label)

    bytes_per_row = 16
    for row_start_index in range(0, len(raw_bytes), bytes_per_row):
        row_bytes = raw_bytes[row_start_index:row_start_index + bytes_per_row]

        offset_string = f"{row_start_index:08X}"

        hex_groups = []
        for group_start in range(0, bytes_per_row, 4):
            group_bytes = row_bytes[group_start:group_start + 4]
            if group_bytes:
                hex_groups.append(" ".join(f"{single_byte:02X}" for single_byte in group_bytes))
            else:
                hex_groups.append("")

        hex_section = "  ".join(hex_groups)
        hex_section_padded = hex_section.ljust(48)

        printable_characters = ""
        for single_byte in row_bytes:
            if 32 <= single_byte <= 126:
                printable_characters += chr(single_byte)
            else:
                printable_characters += "."

        output_lines.append(f"{offset_string}  {hex_section_padded}  {printable_characters}")

    return "\n".join(output_lines)


def print_hex_dump(raw_bytes, direction):
    byte_count = len(raw_bytes)
    label = f"{direction} {byte_count} bytes"
    formatted_output = format_hex_dump(raw_bytes, label)
    print(formatted_output)