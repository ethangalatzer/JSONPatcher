import json
import click


# Checks if the path points to an existent value, a nonexistent value, or an array
def check_path(json_data, path):
    json_traverser = json_data
    for key in path:
        if type(json_traverser) == dict and key in json_traverser:
            json_traverser = json_traverser[key]
        else:
            return "non"
    if type(json_traverser) == list:
        return "arr"
    return "key"


# Modifies the value at the path into the new_value
def modify(json_data, path, new_value):
    path_validity = check_path(json_data, path)
    # Checks that path points to an existent value
    if path_validity == "non":
        click.echo(f"Value at {'.'.join(path)} does not exist")
        raise ValueError
    json_traverser = json_data
    for key in path:
        if key == path[-1]:
            json_traverser[key] = new_value
            break

        json_traverser = json_traverser[key]
    return json_data


# Adds the value at the path into the new_value (same as modify when not a list)
def add(json_data, path, new_value):
    path_validity = check_path(json_data, path)
    # Checks that path points to a nonexistent value
    if path_validity == "key":
        click.echo(f"Value at {'.'.join(path)} already exists")
        raise ValueError
    json_traverser = json_data
    for key in path:
        if key == path[-1]:
            if key in json_traverser and type(json_traverser[key]) == list:
                json_traverser[key].append(new_value)
                break
            json_traverser[key] = new_value
            break
        if key not in json_traverser:
            json_traverser[key] = {}
        json_traverser = json_traverser[key]
    return json_data


# Deletes the value at the path, or all instances of the value when in an array
def delete(json_data, path, value=None):
    path_validity = check_path(json_data, path)
    # Checks that path points to an existent value
    if path_validity == "non":
        click.echo(f"Value at {'.'.join(path)} does not exist")
        raise ValueError
    json_traverser = json_data
    for key in path:
        if key == path[-1]:
            if type(json_traverser[key]) == list and value is not None:
                while value in json_traverser[key]:
                    json_traverser[key].remove(value)
                break
            json_traverser.pop(key)
            break
        json_traverser = json_traverser[key]
    return json_data


# Gets all needed values from operation
def operation_values(operation):
    patch_op = operation["op"]
    patch_path = operation["path"]
    patch_path_list = patch_path.split(".")
    if "value" in operation:
        patch_value = operation["value"]
    else:
        patch_value = None
    return patch_op, patch_path, patch_path_list, patch_value


# Returns list of patches sorted by change number
def sort_patches_by_change_number(patch_files: tuple[str, ...]):
    patch_change_numbers = {}
    for patch_file in patch_files:
        try:
            with open(patch_file, "r") as json_patch:
                json_patch_data = json.load(json_patch)
                patch_change_numbers[json_patch_data["change_number"]] = patch_file
        except FileNotFoundError:
            click.echo(f"Patch {patch_file} does not exist")
            raise FileNotFoundError
        except:
            click.echo(f"Patch {patch_file} is invalid")
            raise Exception
    # Sorts by change number, then returns the file names in order as a list
    return list(dict(sorted(patch_change_numbers.items())).values())


# Click decorators
@click.command()
@click.option("--input", 'input_file', type=str, prompt=True, help="Input JSON file", required=True,)
@click.option("--patch", 'patch_files', type=str, prompt=True, help="Patch JSON file(s), write --patch (file) for each", required=True,
              multiple=True)
@click.option("--output", 'output_file', type=str, prompt=True, help="Output JSON file", required=True)
def patch(input_file: str, patch_files: tuple[str], output_file: str):
    try:
        sorted_patches = sort_patches_by_change_number(patch_files)
    except:
        exit()

    try:
        open(input_file, "r").close()
    except FileNotFoundError:
        click.echo(f"Input JSON file {input_file} does not exist")
        exit()
    except:
        click.echo(f"Input JSON file {input_file} is invalid")
        exit()

    # Reads data file
    with open(input_file, "r") as json_input:
        try:
            json_data = json.load(json_input)
        except json.decoder.JSONDecodeError:
            click.echo("Could not read input JSON file")
            exit()

        # Reads patch files in order
        for patch_file in sorted_patches:
            with open(patch_file, "r") as json_patch:

                json_patch_data = json.load(json_patch)
                operations = json_patch_data["operations"]

                # Executes operations in order
                for operation in operations:

                    patch_op, patch_path, patch_path_list, patch_value = operation_values(operation)

                    # Executes operation by case
                    try:
                        match patch_op:
                            case "add":
                                add(json_data, patch_path_list, patch_value)
                            case "modify":
                                modify(json_data, patch_path_list, patch_value)
                            case "delete":
                                delete(json_data, patch_path_list, patch_value)
                            case _:
                                # Forces valid op
                                click.echo("Operation must be add, modify, or delete")
                                exit()
                    except ValueError:
                        exit()

    # Writes to output file
    try:
        with open(output_file, "w") as json_output:
            json.dump(json_data, json_output, indent=4)
            click.echo("JSON successfully patched")
    except:
        click.echo(f"Output JSON file {output_file} could not be written")
        exit()

    return json_data
