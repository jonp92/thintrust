from faker import Faker
import inspect

class sampleData(Faker):
    def __init__(self):
        super().__init__()
        extracted_parts = [item.__class__.__module__.split('.')[2] for item in self.providers]
        #print(extracted_parts)
        subclass_names = []
        for provider in self.providers:
            module = inspect.getmodule(provider)
            for name, obj in inspect.getmembers(module.Provider):
                if '__' not in name and name not in subclass_names and name[0] != '_' and inspect.isfunction(obj):
                    subclass_names.append(name)
        #print(subclass_names)
                
    def create(self, content_type, gen_number):
        creation = []
        for _ in range(gen_number):
            creation.append(getattr(self, content_type)())
        if gen_number == 1:
            #print(creation[0])
            return creation[0]
        else:
            #print(creation)
            return creation
    
    def create_row(self, creation_items, gen_number):
        new_row_dict = {}
        new_rows_list = []
        columns = [column for column in creation_items]
        for column, item_data in creation_items.items():
            new_row_dict[column] = self.create(item_data, gen_number) #getattr(self, item_data)()
            #new_rows_list.append(new_rows[column])
        for row in zip(*new_row_dict.values()):
            row_dict =  dict(zip(columns, row))
            new_rows_list.append(row_dict)
        return new_rows_list
        

if __name__ == '__main__':           
    sd = sampleData()
    provider = input("What type of data would you like to generate: ")
    if not isinstance(provider, str):
        provider = input("Only text values are excepted, please choose a data type to generate: ")
    number_to_generate = int(input("How many items should be generate: "))
    if not isinstance(number_to_generate, int):
        number_to_generate = input("Only integer values are allowed. Please choose how many items to generate: ")
    print(sd.create(provider, number_to_generate))