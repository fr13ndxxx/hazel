import pandas as pd
import xml.etree.ElementTree as ET
import json

class DataParser:
    @staticmethod
    def parse_csv(file_path):
        return pd.read_csv(file_path)

    @staticmethod
    def parse_xlsx(file_path):
        return pd.read_excel(file_path)

    @staticmethod
    def parse_xml(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        return DataParser.xml_to_dataframe(root)

    @staticmethod
    def parse_json(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return pd.json_normalize(data)

    @staticmethod
    def xml_to_dataframe(root):
        all_records = []
        for offer in root.findall('.//offer'):
            record_data = {
                'offer id': offer.get('id'),
                'available': offer.get('available')
            }
            for elem in offer:
                if elem.tag == 'param':
                    record_data[f'{elem.tag} name="{elem.get("name")}"'] = elem.text
                else:
                    record_data[elem.tag] = elem.text
            all_records.append(record_data)
        return pd.DataFrame(all_records)

    @staticmethod
    def parse_file(file_path):
        if file_path.endswith('.csv'):
            return DataParser.parse_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return DataParser.parse_xlsx(file_path)
        elif file_path.endswith('.xml'):
            return DataParser.parse_xml(file_path)
        elif file_path.endswith('.json'):
            return DataParser.parse_json(file_path)
        else:
            raise ValueError('Unsupported file format')

    @staticmethod
    def extract_data_by_arguments(dataframe, arguments):
        # Filter data based on provided arguments
        filtered_data = dataframe.copy()
        for arg, value in arguments.items():
            if arg in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[arg] == value]
        return filtered_data
