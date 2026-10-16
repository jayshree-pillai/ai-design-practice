"""Exercise 03: OOP: Agent Tool Registry.

Keep the implementation within the scope in problem.md.
"""

class Tool:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self,tool):
        if tool.name in self.tools:
            raise ValueError("Tool already registered")
        self.tools[tool.name] = tool

    def get_tool(self,tool_name):
        if tool_name not in self.tools:
            raise ValueError("tool not registered")
        return self.tools[tool_name]

    def execute_tool(self,tool_name,**kwargs):
        try:
            tool = self.get_tool(tool_name)
            result = tool.function(**kwargs)
            return {"success": True, "result": result, "error": None}
        except Exception as ex:
            return {"sucess":False, "result":None, "error":str(ex)}

# sample tools:
def search_company(name):
    return {"id": 1, "name": name}

def get_rating(company_id):
    if company_id != 1:
        raise ValueError("Company not found")
    return {"company_id": company_id, "rating": 4.5}

def main():
    registry = ToolRegistry()
    registry.register_tool(Tool("search_company","Search for a company",search_company))
    registry.register_tool(Tool("get_rating","Get Rating for a company",get_rating))

    print(registry.execute_tool("search_company",name="Acme"))
    print(registry.execute_tool("get_rating",company_id=99))
    # Tool failure and unregistered tool.
    print(registry.execute_tool("get_rating", company_id=99))
    print(registry.execute_tool("unknown_tool"))

if __name__ == "__main__":
    main()