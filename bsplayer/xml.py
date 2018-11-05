class ElementTreeObject:
    __properties__ = {}
    __types__ = {}
    __repr_format__ = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            value_type = self.__types__.get(k, str)
            v = value_type() if v is None else value_type(v)
            setattr(self, k, v)

    @classmethod
    def to_dict(cls, element):
        result = {}
        for xml_property_name, attr_name in cls.__properties__.items():
            result[attr_name] = element.find(xml_property_name).text

        return result

    @classmethod
    def from_element_tree(cls, element):
        element_dict = cls.to_dict(element)
        return cls(**element_dict)

    def __repr__(self):
        return self.__repr_format__.format(**self.__dict__)
