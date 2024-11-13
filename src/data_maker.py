from typing import Any
from variables import PathVariable as path_vars
from datetime import datetime
import random
from nbconvert import MarkdownExporter
import nbformat
import kaggle
import json
import os



class DataMaker:
    def __init__(self) -> None:
        """
        Only declaring a variable to format to Markdown
        """
        
        self.markdown_exporter = MarkdownExporter()
        
        
    def preparations_data_dirs(self) -> None:
        """
        Function checks if folders exist and cleans up with notebooks on new launches
        """
        
        # Create directories in non-existent directories
        for val in [var.value for var in path_vars]:
            if not os.path.exists(val):
                os.mkdir(val)
            
        # If the directory is not empty, clean it
        if len(os.listdir(path_vars.NOTEBOOK_PATH.value)) > 0:
            for file in os.listdir(path_vars.NOTEBOOK_PATH.value):
                if os.path.isfile(os.path.join(path_vars.NOTEBOOK_PATH.value, file)):
                    os.remove(os.path.join(path_vars.NOTEBOOK_PATH.value, file))
                  
                    
    def load_api(self, api: kaggle.KaggleApi) -> None:
        """
        Args:
            api (kaggle.KaggleApi): Activated Kaggle API
        """
        
        self.api = api    
           
                    
    def download_notebook(self, kernel_spec: dict[str, Any]) -> bool:
        """Function to save notebook in JSON format to .ipynb file locally

        Args:
            kernel_spec (dict[str, Any]): Dict with kernel specifications

        Returns:
            bool: The result of downloading the notebook. True as success and False as failure.
        """
        
        try:
            with open(os.path.join(path_vars.NOTEBOOK_PATH.value, f"{kernel_spec['slug']}.ipynb"), "w", encoding="utf-8") as f:
                json.dump(json.loads(kernel_spec["source"]), f, indent=4)
                    
        except Exception as e:
            # TODO Logging
            return False
        
        return True
    
    
    def _notebook_prompt_structure(self, notebook_md: str, kernel_spec: dict[str, Any]) -> str:
        """Function of making a prompt with notebook section

        Args:
            notebook_md (str): Notebook converted to Markdown section
            kernels_spec (dict[str, Any]): Dict with kernel specification

        Returns:
            str: Prompt with <notebook></notebook> tag
        """
        
        return \
        f"""
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
        """


    def _convert_to_markdown(self, current_file: str | Any) -> str | bool:
        """Function that converts .ipynb notepad to Markdown

        Args:
            current_file (str|Any): Name of notebook .ipynb

        Returns:
            str | bool: Notebook in Markdown format
        """
        
        if isinstance(current_file, str):
            if os.path.splitext(current_file)[1] != ".ipynb":
                # TODO Logging
                return False
            
        else:
            # Save selected notebook via st.file_uploader to tmp dir
            content = current_file.getvalue().decode("utf-8")
            notebook = json.loads(content)
            
            for cell in notebook["cells"]:
                if "outputs" in cell:
                    cell["outputs"] = []
                if "execution_count" in cell:
                    cell["execution_count"] = None
                    
            with open(os.path.join(path_vars.TMP_PATH.value, current_file.name), "w", encoding="utf-8") as f:
                json.dump(notebook, f, indent=4, ensure_ascii=False)

            current_file = os.path.join(path_vars.TMP_PATH.value, current_file.name)
        
        try:
            with open(current_file, "r", encoding="utf-8") as f:
                notebook_content = nbformat.read(f, as_version=4)
                body, _ = self.markdown_exporter.from_notebook_node(notebook_content)
        except Exception as e:
            # TODO Logging
            return False

        return body
    
    
    def make_notebook_prompt(self, kernels_spec: list[dict[str, Any]], file_instruction: str, my_notebook = None) -> str | bool:
        """Function that creates the final prompt for the LLM model 

        Args:
            kernels_spec (list[dict[str, Any]]): List of dicts with kernel specification
            file_instruction (str): Name of file with correct prompt
            my_notebook: Select mode of work (generate or improve). Default: None
            
        Returns:
            str | bool: Ready prompt for LLM model
        """
        
        try:
            with open(os.path.join(path_vars.TEMPLATE_PATH.value, file_instruction), "r", encoding="utf-8") as f:
                instruction_prompt = f.read()
        
        except Exception as e:
            # TODO Logging
            return False
        
        if len(instruction_prompt.strip()) == 0:
            # TODO Logging
            return False
        
        full_notebook_prompt = ""
        for spec in kernels_spec:
            current_file = os.path.join(path_vars.NOTEBOOK_PATH.value, f"{spec['slug']}.ipynb")
            if isinstance(notebook_markdown := self._convert_to_markdown(current_file), bool):
                # TODO Logging
                return False
            
            full_notebook_prompt += self._notebook_prompt_structure(notebook_markdown, spec)
        
        if my_notebook:
            if isinstance(my_notebook_md := self._convert_to_markdown(my_notebook), bool):
                # TODO Logging
                return False
            
            my_notebook_prompt = \
            f"""
<my_notebook>
{my_notebook_md}
</my_notebook>

            """ 

            return f"{instruction_prompt}\n{my_notebook_prompt}\n{full_notebook_prompt.strip()}"
            
        return f"{instruction_prompt}\n{full_notebook_prompt.strip()}"
    
    
    def format_kaggle_notebook(self, kaggle_notebook_data: dict[str, Any], template: str) -> str:
        """Function returns formatted md string for each kaggle notebook analyzed

        Args:
            kaggle_notebook_data (dict[str, Any]): Dict after analysis
            template (str): Template for presentation of results

        Returns:
            str: Final format of the template with data filled in
        """
        
        return template.format(
            author = kaggle_notebook_data.get('author', ''),
            name = kaggle_notebook_data.get('name', ''),
            link = kaggle_notebook_data.get('link', ''), 
            votes = kaggle_notebook_data.get('votes'),
            summary = kaggle_notebook_data.get('summary'),
            
            code_complexity = kaggle_notebook_data.get('code_characteristics', {}).get('code_complexity'),
            code_organization = kaggle_notebook_data.get('code_characteristics', {}).get('code_organization'),
            maintainability = kaggle_notebook_data.get('code_characteristics', {}).get('maintainability'),
            documentation = kaggle_notebook_data.get('code_characteristics', {}).get('documentation'),
            reusability = kaggle_notebook_data.get('code_characteristics', {}).get('reusability'),
            
            unique_features = '<br> **-** '.join([str(i) for i in kaggle_notebook_data.get('approach_analysis', {}).get('unique_features', [])]),
            interesting_tricks = '<br> **-** '.join([str(i) for i in kaggle_notebook_data.get('approach_analysis', {}).get('interesting_tricks', [])]),
            innovative_solutions = '<br> **-** '.join([str(i) for i in kaggle_notebook_data.get('approach_analysis', {}).get('innovative_solutions', [])]),
            
            hidden_gems = '<br> **-** '.join([str(i) for i in kaggle_notebook_data.get('insights', {}).get('hidden_gems', [])]),
            clever_solutions = '<br> **-** '.join([str(i) for i in kaggle_notebook_data.get('insights', {}).get('clever_solutions', [])]),
            overlooked_opportunities = '<br> **-** '.join([str(i) for i in kaggle_notebook_data.get('insights', {}).get('overlooked_opportunities', [])]),
            
            strengths = '<br> ✔️ '.join([str(i) for i in kaggle_notebook_data.get('strengths', [])]),
            weaknesses = '<br> ❌ '.join([str(i) for i in kaggle_notebook_data.get('weaknesses', [])]),
            proposed_improvements = '<br> 📈 '.join([str(i) for i in kaggle_notebook_data.get('proposed_improvements', [])])
        )
    
    
    def format_generated_notebook(self, generated_notebook_data: dict[str, Any], template: str) -> str:
        """Function returns formatted md string for generated notebook

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
    
    
    def format_improved_notebook(self, improved_notebook_data: dict[str, Any], template: str) -> str:
        """Function returns formatted md string for improved notebook

        Args:
            improved_notebook_data (dict[str, Any]): Dict after creating by LLM
            template (str): Template for presentation of results

        Returns:
            str: Final format of the template with data filled in
        """
        
        analysis_data_text = "## 📈 Element Analysis\n\n"
        for analysis_data in improved_notebook_data.get("element_analysis", []):
            analysis_data_text += f"### 🧩 {analysis_data.get('element')}\n\n"
            analysis_data_text += f"✏️ {analysis_data.get('description')}\n\n"
            analysis_data_text += f"🔎 {analysis_data.get('analysis_details')}\n\n"
            
            analysis_data_text += "#### 💡 Suggestions For Improvement\n\n"
            analysis_data_text += f"🚨 **Severity:** {analysis_data.get('suggestions_for_improvement', {}).get('severity')}\n\n"
            analysis_data_text += f"🐞 **Issue:** {analysis_data.get('suggestions_for_improvement', {}).get('issue')}\n\n"
            analysis_data_text += f"🤔 **Suggestion:** {analysis_data.get('suggestions_for_improvement', {}).get('suggestion')}\n\n"
            analysis_data_text += f"💻 **Example:**\n {analysis_data.get('suggestions_for_improvement', {}).get('example')}\n\n"
            analysis_data_text += f"🎯 **Expected Outcome:** {analysis_data.get('suggestions_for_improvement', {}).get('expected_outcome')}\n\n"
            
            analysis_data_text += "---\n\n"
        
        return template.format(
            strengths = '<br> ✔️ '.join([str(i) for i in improved_notebook_data.get('strengths', [])]),
            weaknesses = '<br> ❌ '.join([str(i) for i in improved_notebook_data.get('weaknesses', [])]),
            
            unique_features = '<br> **-** '.join([str(i) for i in improved_notebook_data.get('approach_analysis', {}).get('unique_features', [])]),
            interesting_tricks = '<br> **-** '.join([str(i) for i in improved_notebook_data.get('approach_analysis', {}).get('interesting_tricks', [])]),
            innovative_solutions = '<br> **-** '.join([str(i) for i in improved_notebook_data.get('approach_analysis', {}).get('innovative_solutions', [])]),
            
            code_complexity = improved_notebook_data.get('code_characteristics', {}).get('code_complexity'),
            code_organization = improved_notebook_data.get('code_characteristics', {}).get('code_organization'),
            maintainability = improved_notebook_data.get('code_characteristics', {}).get('maintainability'),
            documentation = improved_notebook_data.get('code_characteristics', {}).get('documentation'),
            reusability = improved_notebook_data.get('code_characteristics', {}).get('reusability'),
            
            analysis = analysis_data_text,
            positive_aspects = '<br> **-** '.join([str(i) for i in improved_notebook_data.get('feedback', {}).get('positive_aspects', [])]),
            areas_for_improvement = '<br> **-** '.join([str(i) for i in improved_notebook_data.get('feedback', {}).get('areas_for_improvement', [])]),
        
            summary = improved_notebook_data.get('implementation_notes')
        )
        
    def save_new_markdown(self, markdown_text: str, improved: bool = False) -> bool:
        """Function save markdown string to file

        Args:
            markdown_text (str): Markdown to save - generated or improved
            improved (bool, optional): Decide if LLM returned new notebook or it just improved one. Defaults to False.

        Returns:
            bool: Confirmation of successful save
        """
        
        mode = "improved" if improved else "generated"
        try:
            with open(os.path.join(path_vars.SAVE_PATH.value, f"md-{mode}-{random.randint(100, 99999)}-{datetime.now().date()}.md"), "w", encoding="utf-8") as f:
                f.write(markdown_text)
        except Exception as e:
            # TODO Logging
            return False
        
        return True