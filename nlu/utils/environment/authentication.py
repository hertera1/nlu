from nlu.utils.environment.env_utils import *


def import_or_install_licensed_lib(JSL_SECRET, lib='healthcare'):
    """ Install Spark-NLP-Healthcare PyPI Package in current environment if it cannot be imported and license
    provided """
    import importlib
    hc_module_name = 'sparknlp_jsl'
    hc_pip_package_name = 'spark-nlp-jsl'
    hc_display_name = ' Spark NLP for Healthcare'
    ocr_pip_package_name = 'spark-ocr'
    ocr_module_name = 'sparkocr'
    ocr_display_name = ' Spark OCR'

    lib_version = JSL_SECRET.split('-')[0]
    if lib == 'healthcare':
        target_import = hc_module_name
        target_install = hc_pip_package_name
        display_name = hc_display_name
    elif lib == 'ocr':
        target_import = ocr_module_name
        target_install = ocr_pip_package_name
        display_name = ocr_display_name
        # OCR version is suffixed with spark version
        if is_env_pyspark_2_3():
            lib_version = lib_version + '+spark23'
        if is_env_pyspark_2_4():
            lib_version = lib_version + '+spark24'
        if is_env_pyspark_3_0() or is_env_pyspark_3_1():
            lib_version = lib_version + '+spark30'

    else:
        raise ValueError(f'Invalid install licensed install target ={lib}')

    try:
        # Try importing, if it fails install the pacakge
        importlib.import_module(target_import)
    except ImportError:
        # Install package since its missing
        import pip
        print(f"{display_name} could not be imported. Installing latest {target_install} PyPI package via pip...")
        import pyspark
        pip_major_version = int(pip.__version__.split('.')[0])
        if pip_major_version in [10, 18, 19, 20]:
            # for these versions pip module does not support installing from Python, we install via OS command.
            os.system(
                f'{sys.executable} -m pip install {target_install}=={lib_version} --extra-index-url https://pypi.johnsnowlabs.com/{JSL_SECRET}')
        else:
            pip.main(['install', f'{target_install}=={lib_version}', '--extra-index-url',
                      f'https://pypi.johnsnowlabs.com/{JSL_SECRET}'])
    finally:
        # Import module after installing package
        import site
        from importlib import reload
        reload(site)
        globals()[target_import] = importlib.import_module(target_import)


def authenticate_enviroment_HC(SPARK_NLP_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
    """Set Secret environ variables for Spark Context"""
    os.environ['SPARK_NLP_LICENSE'] = SPARK_NLP_LICENSE
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY


def authenticate_enviroment_OCR(SPARK_OCR_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
    """Set Secret environ variables for Spark Context"""
    os.environ['SPARK_OCR_LICENSE'] = SPARK_OCR_LICENSE
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY


def authenticate_enviroment_HC_and_OCR(SPARK_NLP_LICENSE, SPARK_OCR_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
    """Set Secret environ variables for Spark Context"""
    authenticate_enviroment_HC(SPARK_NLP_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    authenticate_enviroment_OCR(SPARK_OCR_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)


def get_authenticated_spark_HC(HC_LICENSE, HC_SECRET, AWS_ACCESS_KEY, AWS_SECRET_KEY, gpu):
    import_or_install_licensed_lib(HC_SECRET, 'healthcare')
    authenticate_enviroment_HC(HC_LICENSE, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    import sparknlp
    import sparknlp_jsl
    params = {"spark.driver.memory": "16G",
              "spark.kryoserializer.buffer.max": "2000M",
              "spark.driver.maxResultSize": "2000M"}

    if is_env_pyspark_2_3():
        return sparknlp_jsl.start(HC_SECRET, spark23=True, gpu=gpu, public=sparknlp.version(), params=params)
    if is_env_pyspark_2_4():
        return sparknlp_jsl.start(HC_SECRET, spark24=True, gpu=gpu, public=sparknlp.version(), params=params)
    if is_env_pyspark_3_0() or is_env_pyspark_3_1():
        return sparknlp_jsl.start(HC_SECRET, gpu=gpu, public=sparknlp.version(), params=params)
    raise ValueError(f"Current Spark version {get_pyspark_version()} not supported!")


def get_authenticated_spark_OCR(OCR_LICENSE, OCR_SECRET, AWS_ACCESS_KEY, AWS_SECRET_KEY, gpu):
    import_or_install_licensed_lib(OCR_SECRET, 'ocr')
    authenticate_enviroment_OCR(OCR_LICENSE, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    import sparkocr
    import sparknlp
    params = {"spark.driver.memory": "16G", "spark.kryoserializer.buffer.max": "2000M",
              "spark.driver.maxResultSize": "2000M"}
    OS_version = sparknlp.version()
    spark = sparkocr.start(secret=OCR_SECRET, nlp_version=OS_version, )
    spark.sparkContext.setLogLevel('ERROR')


def get_authenticated_spark_HC_and_OCR(HC_LICENSE, HC_SECRET, OCR_LICENSE, OCR_SECRET, AWS_ACCESS_KEY, AWS_SECRET_KEY,
                                       gpu):
    import_or_install_licensed_lib(HC_SECRET, 'healthcare')
    import_or_install_licensed_lib(OCR_SECRET, 'ocr')
    authenticate_enviroment_HC_and_OCR(HC_LICENSE, OCR_LICENSE, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    import sparkocr
    import sparknlp
    params = {"spark.driver.memory": "16G", "spark.kryoserializer.buffer.max": "2000M",
              "spark.driver.maxResultSize": "2000M"}

    HC_version = HC_SECRET.split('-')[0]
    OS_version = sparknlp.version()
    spark = sparkocr.start(secret=OCR_SECRET, nlp_secret=HC_SECRET, nlp_version=OS_version, nlp_internal=HC_version)
    spark.sparkContext.setLogLevel('ERROR')


def get_authenticated_spark(SPARK_NLP_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, JSL_SECRET, gpu=False, ):
    """
    Authenticates environment if not already done so and returns Spark Context with Healthcare Jar loaded
    0. If no Spark-NLP-Healthcare, install it via PyPi
    1. If not auth, run authenticate_enviroment()

    """
    import sparknlp
    authenticate_enviroment_HC(SPARK_NLP_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    import_or_install_licensed_lib(JSL_SECRET)
    import sparknlp_jsl
    params = {"spark.driver.memory": "16G",
              "spark.kryoserializer.buffer.max": "2000M",
              "spark.driver.maxResultSize": "2000M"}
    if is_env_pyspark_2_3():
        return sparknlp_jsl.start(JSL_SECRET, spark23=True, gpu=gpu, params=params)
    if is_env_pyspark_2_4():
        return sparknlp_jsl.start(JSL_SECRET, spark24=True, gpu=gpu, params=params)
    if is_env_pyspark_3_0() or is_env_pyspark_3_1():
        return sparknlp_jsl.start(JSL_SECRET, gpu=gpu, public=sparknlp.version(), params=params)
    raise ValueError(f"Current Spark version {get_pyspark_version()} not supported!")


def is_authorized_environment():
    """Check if auth secrets are set in environment"""
    SPARK_NLP_LICENSE = os.getenv('SPARK_NLP_LICENSE')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    return None not in [SPARK_NLP_LICENSE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]
