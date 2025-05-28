from typing import Any
from google import genai
from google.genai import types
import json
from json_repair import repair_json


class LLM:
    def __init__(self) -> None:
        self.is_connected = None
    
    
    def connect_client(self, api_key: str) -> None:
        """
        Create a client object with the specified API Key

        Args:
            api_key (str): API Key from Google AI Studio
        """

        self.client = genai.Client(api_key=api_key)
        self.is_connected = True

    
    def get_models_list(self) -> list[str | None]:
        """
        Get models from the API that have 'generateContent' and 'countTokens' functions

        Returns:
            list[str | None]: List of selected models
        """
        assert self.is_connected is True, "First, connect to the API"
        
        return [
            model.name
            for model in self.client.models.list()
            if "generateContent" in model.supported_actions and "countTokens" in model.supported_actions # type: ignore
        ]


    def get_model_parameters(self, model_name: str) -> dict[str, Any] | None:
        """
        It retrieves the model parameters based on the given model name \\
        It returns only the maximum number of input and output tokens

        Args:
            model_name (str): Name of selected model

        Returns:
            dict[str, Any] | None: Information on token limits
        """
        assert self.is_connected is True, "First, connect to the API"

        for model in list(self.client.models.list()):

            model_dict_data = model.__dict__
            if model_dict_data["name"] == model_name:
                return {
                    "max_input_tokens" : model_dict_data["input_token_limit"],
                    "max_output_tokens" : model_dict_data["output_token_limit"]
                }
            

    def count_tokens(self, model_name: str, prompt: str) -> int | None:
        """
        Count tokens in a given prompt according to the selected model

        Args:
            model_name (str): Name of selected model
            prompt (str): Prompt to count tokens

        Returns:
            int | None: Number of tokens from a given prompt
        """
        assert self.is_connected is True, "First, connect to the API"

        return self.client.models.count_tokens(
            model=model_name,
            contents=prompt,
        ).total_tokens
    
    
    def _format_output(self, response: str) -> dict[str, Any] | bool:
        """
        Function formats response from LLM model

        Args:
            response (str): LLM model response

        Returns:
            dict[str, Any] | bool: JSON with data or bool (False) as signal of error
        """
        
        start = response.find("{")
        end = response.rfind("}")
        if start == -1 or end == -1:
            return False
        
        json_response = response[start : end + 1]
        
        return json.loads(repair_json(json_response))
    
    
    def generate_notebook(self, model_name: str, prompt: str, **kwargs) -> dict[str, Any] | bool:
        """
        Function can generate new response (notebook) based on given prompt

        Args:
            model_name (str): Name of selected model
            prompt (str): Prompt to generate a response by model

        Returns:
            dict[str, Any] | bool: Ready, formatted repository or bool (False) as error
        """
        assert self.is_connected is True, "First, connect to the API"

        model_config = {
            "temperature" : 0.2,
            "top_p" : 0.8,
            "top_k" : 32,
            "candidate_count" : 1,
            "max_output_tokens" : 8192,
        }
        model_config.update(kwargs)

        llm_model_response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**model_config)
        )

        if isinstance(formated_output := self._format_output(llm_model_response.text), bool): # type: ignore
            return False
        
        if not isinstance(formated_output, dict) or formated_output.get("new_notebook", None) is None:
            return False

        return formated_output
    
