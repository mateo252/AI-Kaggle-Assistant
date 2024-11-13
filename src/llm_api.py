from typing import Any
import google.generativeai as genai
import time
import json
from json_repair import repair_json



class ApiLLM:
    def __init__(self) -> None:
        pass
    
    
    def load_model(self, model_name: str) -> None:
        """Load selected model by name

        Args:
            model_name (str): Name of selected model
        """
        
        self.llm_model = genai.GenerativeModel(model_name, system_instruction="You are a professional data analyst with many years of experience and have knowledge of mathematics and computer science.")
    
    
    def get_models_list(self) -> list[Any]:
        """Function returns a list of LLM models that support generation methods

        Returns:
            list[Any]: List with parameters of a specific model
        """
        
        return genai.list_models()
    
    
    def get_count_tokens(self, text: str) -> int:
        """Function returns the number of tokens for the given text

        Args:
            text (str): Text for token counting

        Returns:
            int: Number of tokens
        """
        
        return self.llm_model.count_tokens(text).total_tokens
    
    
    def _format_output(self, response: str) -> dict[str, Any] | bool:
        """Function formats response from LLM model

        Args:
            response (str): LLM model response

        Returns:
            dict[str, Any] | bool: JSON with data or bool (False) as signal of error
        """
        
        start = response.find("{")
        end = response.rfind("}")
        if start == -1 or end == -1:
            # TODO Logging
            return False
        
        json_response = response[start : end + 1]
        
        return json.loads(repair_json(json_response)) # type: ignore
    
    
    def generate_output(self, prompt: str, improve_notebook: bool = False, **kwargs) -> tuple | bool:
        """Function uses selected model to generate output

        Args:
            prompt (str): Prompt for model LLM
            improve_notebook (bool, optional): Detect which data get from model response. Defaults to False.

        Returns:
            tuple | bool: Tuple with data or bool (False) as signal of error
        """

        model_config = {
            "temperature" : 0.2,
            "top_p" : 0.8,
            "top_k" : 32,
            "candidate_count" : 1,
            "max_output_tokens" : 8192,
        }
        model_config.update(kwargs)

        start_time = time.time()
        llm_model_response = self.llm_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(**model_config)
        )
        response_time = time.time() - start_time
        
        model_stats = {
            "model_prompt_token_count" : str(int(llm_model_response.usage_metadata.prompt_token_count)),
            "model_candidates_token_count" : str(int(llm_model_response.usage_metadata.candidates_token_count)),
            "model_total_token_count" : str(int(llm_model_response.usage_metadata.total_token_count)),
            "response_time" : str(round(response_time, 2))
        }

        if isinstance(formated_output := self._format_output(llm_model_response.text), bool):
            # TODO Logging
            return False
        
        if not isinstance(formated_output, dict):
            # TODO Logging
            return False
        
        if improve_notebook:
            if formated_output.get("notebook_analyses", None) is None or formated_output.get("improved_notebook", None) is None:
                # TODO Logging
                return False
        
        elif formated_output.get("notebook_analyses", None) is None or formated_output.get("new_notebook", None) is None:
            # TODO Logging
            return False
        
        return formated_output, model_stats