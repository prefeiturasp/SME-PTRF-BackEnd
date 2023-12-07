import os


def list_files_in_mypy_list(file_list_path, apps_dir):
    """
    Lista arquivos especificados no arquivo file_list_path relacionados a apps_dir.
    """
    with open(file_list_path, "r") as file:
        return set(line.strip().replace(apps_dir, "") for line in file if line.strip())


def count_python_files(directory, mypy_files_set):
    """
    Conta o total de arquivos Python e quantos estão no conjunto mypy_files_set dentro do diretório.
    """
    total_files = 0
    typed_files = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                total_files += 1
                full_path = os.path.join(root, file)

                normalized_path = full_path.replace(directory, "")

                if normalized_path in mypy_files_set:
                    typed_files += 1
    return total_files, typed_files


def main():
    APPS_DIR = "sme_ptrf_apps"
    project_path = os.path.join(os.getcwd(), APPS_DIR)
    mypy_file_list = "check_types_in.txt"

    if not os.path.exists(project_path):
        print(f"Caminho do projeto {project_path} não existe.")
        return

    mypy_files_set = list_files_in_mypy_list(mypy_file_list, APPS_DIR)
    total_python_files, total_typed_files = count_python_files(
        project_path, mypy_files_set
    )

    print(f"Total de Arquivos Python: {total_python_files}")
    print(f"Arquivos Python na Lista Mypy: {total_typed_files}")
    if total_python_files > 0:
        print(f"Cobertura de Type Hints: {total_typed_files / total_python_files * 100:.2f}%")
    else:
        print("Nenhum arquivo Python encontrado.")


if __name__ == "__main__":
    main()
