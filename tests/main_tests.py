import requests

URL = 'http://127.0.0.1:8000/api'
HEADERS = {"Content-Type": "application/xml"}


def test_post_without_arguments_check_status_code_equals_200():  # test_function1
    xml_body = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function1</methodName>
    <params>
    </params>
</methodCall>'''
    response = requests.post(URL, data=xml_body, headers=HEADERS)
    assert response.status_code == 200


def test_post_with_one_required_and_optional_arguments_check_status_code_equals_200():  # test_function5
    xml_body_all_args = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function5</methodName>
    <params>
        <param>
            <value>
                <string>
                    Tolik
                </string>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Demchuk
                </string>
            </value>
        </param>
    </params>
</methodCall>'''
    response_all_args = requests.post(URL, data=xml_body_all_args, headers=HEADERS)
    xml_body_one_arg = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function5</methodName>
    <params>
        <param>
            <value>
                <string>
                    Tolik
                </string>
            </value>
        </param>
    </params>
</methodCall>'''
    response_one_arg = requests.post(URL, data=xml_body_one_arg, headers=HEADERS)
    assert response_all_args.status_code == 200 and response_one_arg.status_code == 200


def test_post_with_base_model_body_check_status_code_equals_200():  # test_function2
    xml_body = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function2</methodName>
    <params>
        <param>
            <value>
                <struct>
                    <member>
                        <name>name</name>
                        <value>
                            <string>
                                Minecraft Game
                            </string>
                        </value>
                    </member>
                    
                    <member>
                        <name>count</name>
                        <value>
                            <int>
                                1234
                            </int>
                        </value>
                    </member>
                </struct>
            </value>
        </param>
    </params>
</methodCall>'''
    response = requests.post(URL, data=xml_body, headers=HEADERS)
    assert response.status_code == 200


def test_post_with_two_base_models_body_check_status_code_equals_200():  # test_function3
    xml_body = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function3</methodName>
    <params>
        <param>
            <value>
                <struct>
                    <member>
                        <name>name</name>
                        <value>
                            <string>
                                Minecraft Game
                            </string>
                        </value>
                    </member>

                    <member>
                        <name>count</name>
                        <value>
                            <int>
                                1234
                            </int>
                        </value>
                    </member>
                </struct>
            </value>
        </param>

        <param>
            <value>
                <struct>
                    <member>
                        <name>age</name>
                        <value>
                            <int>
                                17
                            </int>
                        </value>
                    </member>

                    <member>
                        <name>year</name>
                        <value>
                            <int>
                                2003
                            </int>
                        </value>
                    </member>
                </struct>
            </value>
        </param>
    </params>
</methodCall>'''
    response = requests.post(URL, data=xml_body, headers=HEADERS)
    assert response.status_code == 200


def test_post_with_one_base_model_one_required_and_one_optional_args_check_status_code_equals_200():  # test_function4
    xml_body_all_args = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function4</methodName>
    <params>
        <param>
            <value>
                <struct>
                    <member>
                        <name>age</name>
                        <value>
                            <int>
                                17
                            </int>
                        </value>
                    </member>

                    <member>
                        <name>year</name>
                        <value>
                            <int>
                                2003
                            </int>
                        </value>
                    </member>
                </struct>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Tolik
                </string>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Demchuk
                </string>
            </value>
        </param>
    </params>
</methodCall>'''
    response_all_args = requests.post(URL, data=xml_body_all_args, headers=HEADERS)
    xml_without_optional = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function4</methodName>
    <params>
        <param>
            <value>
                <struct>
                    <member>
                        <name>age</name>
                        <value>
                            <int>
                                17
                            </int>
                        </value>
                    </member>

                    <member>
                        <name>year</name>
                        <value>
                            <int>
                                2003
                            </int>
                        </value>
                    </member>
                </struct>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Tolik
                </string>
            </value>
        </param>
    </params>
</methodCall>'''
    response_without_optional = requests.post(URL, data=xml_without_optional, headers=HEADERS)
    assert response_all_args.status_code == 200 and response_without_optional.status_code == 200


def test_post_with_two_base_models_and_two_args_check_status_code_equals_200():  # test_function
    xml_body = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function</methodName>
    <params>
        <param>
            <value>
                <struct>
                    <member>
                        <name>age</name>
                        <value>
                            <int>
                                17
                            </int>
                        </value>
                    </member>

                    <member>
                        <name>year</name>
                        <value>
                            <int>
                                2003
                            </int>
                        </value>
                    </member>
                </struct>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Vlad
                </string>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Demchuk
                </string>
            </value>
        </param>

    </params>
</methodCall>'''
    response = requests.post(URL, data=xml_body, headers=HEADERS)
    assert response.status_code == 200

