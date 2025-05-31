from typing import Any
import kaggle



class MyKaggleApi:

    def __init__(self) -> None:
        pass
    
    
    def load_api(self, api: kaggle.KaggleApi) -> None:
        """
        Simply declare the API object to the variable

        Args:
            api (kaggle.KaggleApi): Activated Kaggle API
        """
        
        self.api = api
    
    
    def get_kernels_list(self, competition: str | None = None, 
                         dataset: str | None = None,
                         **kwargs)-> Any:
        """
        Function that retrieves kernel (notebook) name based on request configuration

        Args:
            competition (str | None, optional): Name of the competition from which to download notebooks. Defaults to None.
            dataset (str | None, optional): Name of the dataset from which to download notebooks. Defaults to None.
        
        Returns:
            list: List with kernels from api responses
        """
        assert not (competition is None and dataset is None), "Chose competition or dataset. Both None"
        assert not (competition is not None and dataset is not None), "Chose competition or dataset. Both has value"

        # Default settings for api request
        default_settings = {
            "page"      : 1,
            "page_size" : 20,
            "language"  : "python",
            "sort_by"   : "voteCount"
        }
        default_settings.update(kwargs)

        # Dict with final settings for api request
        kernels_config = {"dataset" : dataset} if competition is None else {"competition" : competition}
        kernels_config.update(default_settings)
        
        try:
            kernels_name_list = self.api.kernels_list(**kernels_config) # type: ignore
        
        except Exception as e:
            return []
        
        return kernels_name_list
    

    def get_kernels_specification(self, kernels: list) -> list[dict[str, Any]]:
        """
        Function to get specification of each kernel

        Args:
            kernels (list): List with kernels

        Returns:
            list[dict[str, Any]]: List with dicts of the name of the kernel specification and the value of this specification
        """
        assert len(kernels) > 0, "No kernels to use"
        
        kernels_spec_list = []
        for kernel in kernels:
            kernel_name = kernel.ref # type: ignore
            
            user_name = kernel_name.split("/")[0]
            notebook_name = kernel_name.split("/")[1]
            
            try:
                request_kernel = self.api.kernel_pull(user_name=user_name, kernel_slug=notebook_name) 
                kernels_spec_list.append({
                    "author"                 : request_kernel["metadata"]["author"],
                    "categoryIds"            : request_kernel["metadata"]["categoryIds"],
                    "competitionDataSources" : request_kernel["metadata"]["competitionDataSources"],
                    "datasetDataSources"     : request_kernel["metadata"]["datasetDataSources"],
                    "language"               : request_kernel["metadata"]["language"],
                    "title"                  : request_kernel["metadata"]["title"],
                    "slug"                   : request_kernel["metadata"]["slug"],
                    "link"                   : f"https://www.kaggle.com/code/{kernel_name}",
                    "totalVotes"             : request_kernel["metadata"]["totalVotes"],
                    "source"                 : request_kernel["blob"]["source"],
                })
    
            except Exception as e:
                return []
                
        return kernels_spec_list