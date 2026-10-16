"""Exercise 02: OOP: External Company API.

Not implemented yet. Complete design.md before writing the first solution.
Keep the implementation within the scope in problem.md.
"""

import requests 

class Company:
    def __init__(self,id,name,industry,rating):
        self.id = id
        self.name = name
        self.industry = industry
        self.rating = rating

class CompanyClient:
    def __init__(self,url):
        self.url = url
        self.companies = {}

    def get_companies(self,min_rating):
        response = requests.get(self.url,timeout=10)
        if response.status_code != 200:
            raise requests.HTTPError(f"API status error{response.status_code}")
        records= response.json()
        for record in records:
            c = Company(record["id"],record["name"],record["industry"], record["rating"])
            if c.id not in self.companies:
                self.companies[c.id] = c
        matches = [ c for c in self.companies.values() if c.rating > min_rating]

        def rating_score(company):
            return company.rating
        return sorted(matches,key = rating_score,reverse=True)
def main():
    cc = CompanyClient("www.get_company.com")
    for c in cc.get_companies(3):
        print(f"The Company name is{c.name0}")
if __name__== "__main__":
    main()