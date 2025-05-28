from typing import Any
from config import PathVariable
from datetime import datetime
from nbconvert import MarkdownExporter
import nbformat
import textwrap
import json
import os



class DataMaker:

    def __init__(self) -> None:
        self.markdown_exporter = MarkdownExporter()
        
        
    def prepare_data_dir(self) -> None:
        """
        Function checks if folders exist and cleans up with notebooks on new launches
        """
        
        # Create directories in non-existent directories
        for dir_path in [path_value.value for path_value in PathVariable]:
            os.makedirs(dir_path, exist_ok=True)
            
        # If the directory is not empty, clean it
        NOTEBOOK_PATH = PathVariable.NOTEBOOK_PATH.value
        if os.listdir(NOTEBOOK_PATH):
            for file in os.listdir(NOTEBOOK_PATH):
                if os.path.isfile(os.path.join(NOTEBOOK_PATH, file)):
                    os.remove(os.path.join(NOTEBOOK_PATH, file))
                  
                    
    def download_notebook(self, kernel_spec: dict[str, Any]) -> bool:
        """
        Function to save notebook in JSON format to .ipynb file locally
        From this notebook, a prompt is created for the model

        Args:
            kernel_spec (dict[str, Any]): Dict with kernel specifications

        Returns:
            bool: The result of downloading the notebook. True as success and False as failure.
        """
        
        try:
            with open(os.path.join(PathVariable.NOTEBOOK_PATH.value, f"{kernel_spec['slug']}.ipynb"), "w", encoding="utf-8") as f:
                json.dump(json.loads(kernel_spec["source"]), f, indent=4)
                    
        except Exception as e:
            return False
        
        return True
    
    
    def _make_notebook_prompt_structure(self, notebook_md: str, kernel_spec: dict[str, Any]) -> str:
        """Function of making a prompt with notebook section

        Args:
            notebook_md (str): Notebook converted to Markdown section
            kernels_spec (dict[str, Any]): Dict with kernel specification

        Returns:
            str: Prompt with <notebook></notebook> tag
        """
        
        return textwrap.dedent(f"""
            <notebook>
            <author>
            {kernel_spec['author']}
            </author>
            <title>
            {kernel_spec['title']}
            </title>
            <link>
            {kernel_spec['link']}
            </link>
            <category>
            {kernel_spec['categoryIds']}
            </category>
            <language>
            {kernel_spec['language']}
            </language>
            <votes>
            {kernel_spec['totalVotes']}
            </votes>
            <code>
            {notebook_md.strip()}
            </code>
            </notebook>
        """)


    def _convert_ipynb_to_markdown(self, current_file: str | Any) -> str | bool:
        """
        Function that converts .ipynb notebook to Markdown

        Args:
            current_file (str|Any): Name of notebook .ipynb

        Returns:
            str | bool: Notebook in Markdown format
        """
        
        if isinstance(current_file, str):
            if os.path.splitext(current_file)[1] != ".ipynb":
                return False
            
        try:
            with open(current_file, "r", encoding="utf-8") as f:
                notebook_content = nbformat.read(f, as_version=4)
                body, _ = self.markdown_exporter.from_notebook_node(notebook_content)
                
        except Exception as e:
            return False

        return body
    
    
    def make_notebook_generator_prompt(self, kernels_spec: list[dict[str, Any]], file_instruction: str) -> str | bool:
        """
        Function that creates the final prompt for the LLM model
        It combines two parts: instructions from a file and text with information from a notebook

        Args:
            kernels_spec (list[dict[str, Any]]): List of dicts with kernel specification
            file_instruction (str): Name of file with correct prompt
            
        Returns:
            str | bool: Ready prompt for LLM model
        """
        
        try:
            with open(os.path.join(PathVariable.TEMPLATE_PATH.value, file_instruction), "r", encoding="utf-8") as f:
                instruction_prompt = f.read()
        
        except Exception as e:
            return False
        
        # If the instruction prompt could be empty
        if not instruction_prompt.strip():
            return False
        
        full_notebook_prompt_structure = ""
        for spec in kernels_spec:
            current_file = os.path.join(PathVariable.NOTEBOOK_PATH.value, f"{spec['slug']}.ipynb")
            if isinstance(notebook_markdown := self._convert_ipynb_to_markdown(current_file), bool):
                return False
            
            full_notebook_prompt_structure += self._make_notebook_prompt_structure(notebook_markdown, spec)
        
        # Full prompt is: 
        # - instruction from file
        # - notebooks generate by function '_make_notebook_prompt_structure(...)'
        return f"{instruction_prompt}\n{full_notebook_prompt_structure.strip()}"
       
    
    def format_generated_notebook(self, generated_notebook_data: dict[str, Any], template: str) -> str:
        """
        Function returns formatted md string for generated notebook

        Args:
            generated_notebook_data (dict[str, Any]): Dict after creating by LLM
            template (str): Template for presentation of results

        Returns:
            str: Final format of the template with data filled in
        """
        
        # Concat 'Section' from generated notebook in JSON format
        section_data_text = ""
        for section_data in generated_notebook_data.get("sections", []):
            section_data_text += f"### {section_data.get('name')}\n\n"
            section_data_text += f"✏️ {section_data.get('description')}\n\n"
            
            if section_data.get('code'):
                section_data_text += f"```python\n{section_data.get('code')}\n```\n\n"
                
            if section_data.get('explanation'):
                section_data_text += f"📖 {section_data.get('explanation')}\n\n"
                    
            for val in section_data.get("alternatives_considered", []):
                section_data_text += f"🔄 {val}\n\n"
        
        # Concat 'Implemented' from generated notebook in JSON format
        implemented_data_text = "### ⚙️ Optimizations\n\n"
        implemented_data_text += "##### 🎉 Implemented\n\n"
        for val in generated_notebook_data.get("optimizations", {}).get("implemented", []):
            implemented_data_text += f"- {val}\n\n"
        
        # Concat 'Future' from generated notebook in JSON format
        future_data_text = "##### 🔮 Future\n\n"
        for val in generated_notebook_data.get("optimizations", {}).get("future", []):
            future_data_text += f"- {val}\n\n"
        
        # Concat 'Lessons learned' from generated notebook in JSON format
        summary_data_text = "### 📋 Summary\n\n"
        for val in generated_notebook_data.get("lessons_learned", []):
            summary_data_text += f"✔️ {val}\n\n"
        
        return template.format(
            title = f"## {generated_notebook_data.get('title')}",
            section_data = section_data_text,
            implemented = implemented_data_text,
            future = future_data_text,
            summary = summary_data_text
        )
    
           
    def save_new_markdown(self, markdown_text: str, name: str) -> bool:
        """
        Function to save to notebook in markdown format generated by AI
        Location path is set by 'config' file
        There is a security feature so that two notepads do not have the same file name

        Args:
            markdown_text (str): Markdown text generated by AI
            name (str): Name of notebook, it is part of the file name

        Returns:
            bool: Signal if the file has been saved correctly
        """
        
        def sort_files(file: str) -> int | float:
            """
            Simple function takes first number of file name
            It tries to return value as 'int'

            Args:
                file (str): Name of file to sort

            Returns:
                int: Number of file in dir
            """
            try:
                return int(file.split("-")[0])
            
            except Exception:
                return float("inf")


        max_file_number = sorted(
            os.listdir(PathVariable.SAVE_PATH.value),
            key=lambda x: sort_files(x),
            reverse=True
        )[0].split("-")[0]

        try:
            with open(os.path.join(PathVariable.SAVE_PATH.value, f"{int(max_file_number) + 1}-{datetime.now().date()}-{"-".join(name.split(""))}.md"), 
                      "w", encoding="utf-8"
            ) as f:
                f.write(markdown_text)

        except Exception as e:
            return False
        
        return True