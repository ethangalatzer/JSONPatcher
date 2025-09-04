import json
import click


# Checks if the path points to an existent value, a nonexistent value, or an array
def check_path(json, path):
    json_traverser = json
    for key in path:
        if type(json_traverser) == dict and key in json_traverser:
            json_traverser = json_traverser[key]
        else:
            return False
    if type(json_traverser) == list:
        return "arr"
    return True


# Modifies the value at the path into the new_value
def modify(json, path, new_value):
    path_validity = check_path(json, path)
    # Checks that path points to an existent value
    if not path_validity:
        click.echo(f"Value at {'.'.join(path)} does not exist")
        exit()
    json_traverser = json
    for key in path:
        if key == path[-1]:
            json_traverser[key] = new_value
            break
        if key not in json_traverser:
            json_traverser[key] = {}
        json_traverser = json_traverser[key]
    return json

# Adds the value at the path into the new_value (same as modify when not a list)
def add(json, path, new_value):
    path_validity = check_path(json, path)
    # Checks that path points to either a nonexistent value or a list
    if path_validity and path_validity != "arr":
        click.echo(f"Value at {'.'.join(path)} already exists")
        quit()
    json_traverser = json
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
    return json

# Deletes the value at the path, or all instances of the value when in an array
def delete(json, path, value=None):
    path_validity = check_path(json, path)
    # Checks that path points to an existent value
    if not path_validity:
        click.echo(f"Value at {'.'.join(path)} does not exist")
        exit()
    json_traverser = json
    for key in path:
        if key == path[-1]:
            if type(json_traverser[key]) == list and value != None:
                while value in json_traverser[key]:
                    json_traverser[key].remove(value)
                break
            json_traverser.pop(key)
            break
        json_traverser = json_traverser[key]
    return json

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
def sort_patches_by_change_number(patches):
    patch_change_numbers = {}
    for patch in patches:
        try:
            with open(patch, "r") as json_patch:
                json_patch_data = json.load(json_patch)
                patch_change_numbers[json_patch_data["change_number"]] = patch
        except FileNotFoundError:
            click.echo(f"Patch {patch} does not exist")
            exit()
    return(dict(sorted(patch_change_numbers.items())))

# Click decorators
@click.command()
@click.option("--input", type=str, prompt=True, help="Input JSON file", required=True)
@click.option("--patch", type=str, prompt=True, help="Patch JSON file(s), write --patch (file) for each", required=True, multiple=True)
@click.option("--output", type=str, prompt=True, help="Output JSON file", required=True)
def patch(input, patch, output):

    patch_change_numbers = sort_patches_by_change_number(patch)
    try:
        open(input, "r").close()
    except FileNotFoundError:
        click.echo(f"Input JSON file does not exist")
        exit()
    # Reads data file
    with open(input, "r") as json_input:
        try:
            json_data = json.load(json_input)
        except:
            click.echo("Could not read input JSON file")
            exit()

        # Reads patch files in order
        for patch_file in patch_change_numbers:
            with open(patch_change_numbers[patch_file], "r") as json_patch:

                json_patch_data = json.load(json_patch)
                operations = json_patch_data["operations"]

                # Executes operations in order
                for operation in operations:

                    patch_op, patch_path, patch_path_list, patch_value = operation_values(operation)

                    # Executes operation by case
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

    # Writes to output file
    with open(output, "w") as json_output:
        json.dump(json_data, json_output, indent=4)
        click.echo("JSON successfully patched")
    return json_data