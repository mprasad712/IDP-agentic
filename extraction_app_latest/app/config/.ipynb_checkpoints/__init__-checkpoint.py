import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
super_parentdir = os.path.dirname(parentdir)
#print("parent dir  ", super_parentdir)
sys.path.insert(0,super_parentdir) 

class idpSettings:

  def __init__(self):
    #all the base paths  
    BACKEND_BASE_PATH = "/data/digital_workmate_agentic/extraction_app_latest" #path till idp_solution FOLDER
    FRONTENT_BASE_PATH = "/data/digital_workmate_agentic/web_app_latest/backend_web" #PATH TILL IDP FOLDER
    # FRONTENT_BASE_PATH = "/data/web_app_copy/backend"
    MODELS_BASE_PATH = "/data/digitalworkmate/models"  #Models base path  


    self.ROOT_INPUT_DIR = FRONTENT_BASE_PATH + "/invoiceapp/static/eips_data/invoice_data"
    self.ROOT_INPUT_DIR_INPUT_QUEUE = "/data/digital_workmate_agentic/input_queue"
    self.PATTERNS_PATH = FRONTENT_BASE_PATH + "/invoiceapp/static/eips_data/user_active_learning_data"
    self.INVOICE_LOG = BACKEND_BASE_PATH + "/logs/exception_logs"
    self.OUTPUT_DIR = BACKEND_BASE_PATH + "/output_data/ocr_output"
    self.TABLE_OUTPUT= BACKEND_BASE_PATH + "/output_data/table_output"
    
    #ocr
    self.TEMP_RETRUCT_PATH = BACKEND_BASE_PATH + "/output_data/ocr_output/45309525/data_.txt" #this temp file needs to be created manually if doing setup in new server 

    #Multi Invoice##
    self.INVOICE_NUMBER_PATTERN = BACKEND_BASE_PATH + "/app/utilities/patterns/invoice_number.txt"
    self.OUTPUT_PATH = BACKEND_BASE_PATH + "/input_queue/multiinvoice_temp"
    ##Ends##
      
    #####CONTRACTS
    self.CONTRACT_TABLE_OUTPUT= BACKEND_BASE_PATH + "/output_data/contract_output" 
    self.CONTRACT_ML_OUTPUT = BACKEND_BASE_PATH + "/app/nlp/contract/line/ml_extractor/pattern_files"
    self.CONTRACT_OCR_OUTPUT = BACKEND_BASE_PATH + "/output_data/contract_output/ocrmypdf_output_pdf"
    self.CONTRACT_DIGTOTXT_OUTPUT = BACKEND_BASE_PATH + "/output_data/contract_output/text_files_dig"
    ##file- resource_item_inference
    self.CONTRACT_TRAINING_FILES_FEATURE_CLASS_C_RES_ITEM = BACKEND_BASE_PATH + "/app/nlp/contract/header/ml_extractor/training/Chunk/feature_class_label_C_res_item.json"
    self.CONTRACT_INTERMEDIATE_FILES_CHUNK_TEST_DATA_ITEM_RES = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Chunk/test_data_file_res_item_C.json"
    self.CONTRACT_INTERMEDIATE_FILES_CHUNK_CSV_DATA_FILE = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Chunk/data_file_C_res_item.csv"
      
    ##file- data_scan_inference
    self.CONTRACT_FEATURE_CLASS_LABEL_C= BACKEND_BASE_PATH + "/app/nlp/contract/header/ml_extractor/training/Chunk/feature_class_label_C.json"
    self.CONTRACT_TEST_DATA_C = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Chunk/test_data_file_C.json"
    self.CONTRACT_CSV_FILE_C = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Chunk/data_file_C.csv"
    self.CONTRACT_INF_CHUNK = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Chunk/inf_chunk.json"
    self.CONTRACT_CHUNK_JSON = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Chunk/chunk.json"
    ##file- inference_scan
    self.CONTRACT_FEATURE_CLASS_LABEL_WC= BACKEND_BASE_PATH + "/app/nlp/contract/header/ml_extractor/training/Without_Chunk/feature_class_label_WC.json"
    self.CONTRACT_TEST_DATA_WC = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Without_Chunk/test_data_file_WC.json"
    self.CONTRACT_CSV_FILE_WC = BACKEND_BASE_PATH + "/output_data/contract_output/intermediate_files/Without_Chunk/data_file_WC.csv"

      
    self.CONTRACT_TEMP_MODEL_C = MODELS_BASE_PATH + "/contracts/model_checkpoint_chunk/checkpoint-3325"
    self.CONTRACT_TEMP_MODEL_WC = MODELS_BASE_PATH + "/contracts/model_checkpoint_without_chunk/checkpoint-2233"
    self.CONTRACT_SAVED_MODEL_C = MODELS_BASE_PATH + "/contracts/fine_tune_chunk"
    self.CONTRACT_SAVED_MODEL_WC = MODELS_BASE_PATH + "/contracts/fine_tune_without_chunk"
    self.CONTRACT_SAVED_MODEL_IRT = MODELS_BASE_PATH + "/contracts/fine_tune_irt"
    self.CONTRACT_TEMP_MODEL_IRT = MODELS_BASE_PATH + "/contracts/model_checkpoint_irt/checkpoint-630"
    self.CONTRACT_TABLE_PDF_PATH = BACKEND_BASE_PATH + "/output_data/contract_output/table_pdfs"
    self.CONTRACT_TABLE_CSV_OUTPUT = BACKEND_BASE_PATH + "/output_data/contract_output/table_csv"
    self.CONTRACTS_TOPUP_PATTERNS = BACKEND_BASE_PATH + "/app/nlp/contract/header/reg_extractor/pattern_files"
    self.CONTRACT_PATTERN=BACKEND_BASE_PATH+"/app/nlp/contract/line/ml_extractor/pattern_files/pattern.txt"
    self.CONTRACT_RESOURCE_NAME=BACKEND_BASE_PATH+"/app/nlp/contract/line/ml_extractor/pattern_files/Resource_Name.txt"
    self.CONTRACT_ITEM_RATE = BACKEND_BASE_PATH+"/app/nlp/contract/line/ml_extractor/pattern_files/Item_Rate.txt"
    self.CONTRACT_PATTERNS_DICT =  {
            "t_1.txt":BACKEND_BASE_PATH+"/app/nlp/contract/line/ml_extractor/pattern_files/Resource_Name.txt",
            "t_2.txt": BACKEND_BASE_PATH+"/app/nlp/contract/line/ml_extractor/pattern_files/Item_Rate.txt"}
    #####CONTRACTS END

    ###LILT###
    self.LILT_MODEL_15_SCANNED = MODELS_BASE_PATH + "/lilt/model_1_sc"
    self.MODELS_6FIELDS_SCANNED = MODELS_BASE_PATH + "/lilt/model_2_sc/"
    self.MODELS_DIGITAL_6FIELDS = MODELS_BASE_PATH + "/lilt/model_2_dig"
    self.MODELS_FINETUNED_15FIELDS = MODELS_BASE_PATH + "/lilt/model_1_dig/"
    self.NEW_MODEL_SCANNED = MODELS_BASE_PATH + "/lilt/model_3_sc/"
    self.NEW_MODEL_DIGITAL = MODELS_BASE_PATH + "/lilt/model_3_dig/"
    self.ADDRESS_MODEL_DIGITAL = MODELS_BASE_PATH + "/lilt/model_4_dig"
    self.ADDRESS_MODEL_SCANNED = MODELS_BASE_PATH + "/lilt/model_4_sc"
    self.LILT_DIGTOTXT_OUTPUT = BACKEND_BASE_PATH + "/output_data/ocr_output/45309525/finance_configuration_invoices"
    self.LILT_TOPUP_PATTERNS  = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/header/reg_extractor/pattern_files"
    ###LILT ENDS###
      
    self.ACTIVE_LEARNING_TABLE_PATH = FRONTENT_BASE_PATH + '/invoiceapp/static/eips_data/user_active_learning_data/table_configs/'

    ###classifier paths
    self.TAX_INVOICE_CLASSIFIER_PTT = BACKEND_BASE_PATH + "/app/classifier/patterns/patterns.txt"

    # GENAI PATHS
    # self.GENAI_MODEL = MODELS_BASE_PATH + "/llama3.1_instruct"
    self.GENAI_MODEL = "/data/data/harsh/Phi-4"

    #ROTATION MODEL
    self.ROTATION_MODEL = MODELS_BASE_PATH + "/rotation/model.h5"
      


    #INVOICE TABLE PATHS 
    self.TABLE_DETECTION_DETR_MODEL = MODELS_BASE_PATH + "/table_detection/detr"
    self.NAME_MODEL = MODELS_BASE_PATH + "/ner_model"
    self.PATTERN_FILES_DIR = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files"
    self.CUSTOM_GST_PATTERNS = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/custom_gst_patterns_file"
    self.REPEATED_HEADER_FILE = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/splitted_words.txt"
    self.BREAKED_COLUMNS_PTT = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/columns_patterns.txt"
    self.COMBINE_COLUMNS_PTT = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/combine_column.txt"
    self.ENDLINE_KEYWORDS_PTT = BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/endline_keywords.txt"
    self.CUSTOM_VENDOR_JSON = BACKEND_BASE_PATH+"/app/nlp/domestic/traditional_ai/line/reg_extractor/static/vendor_json.json"
    self.SINGLE_PATTERN_FILES_PATHS = {
        'Description.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Description.txt",
        'Hsn code.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Hsn code.txt",
        'Igst value.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Igst value.txt",
        'Igst rate.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Igst rate.txt",
        'Line no.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Line no.txt",
        'Quantity.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Quantity.txt",
        'Unit price.txt': BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Unit price.txt",
        'Cgst value.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Cgst value.txt",
        'Cgst rate.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Cgst rate.txt",
        'Utgst value.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Utgst value.txt",
        'Sgst value.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Sgst value.txt",
        'Sgst rate.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Sgst rate.txt",
        'Vat Category.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Vat category.txt",
        'Vat rate.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Vat rate.txt",
        'line_amount.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/line_amount.txt",
        'Expense start date.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Expense start date.txt",
        'Expense end date.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Expense end date.txt",
        'Gst category.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Gst category.txt",
        'Resource name.txt':BACKEND_BASE_PATH + "/app/nlp/domestic/traditional_ai/line/reg_extractor/static/pattern_files/Resource name.txt"
        }
    self.XML_DIR = os.path.join(self.OUTPUT_DIR, 'XML')
    self.PDF_EXT = ['.pdf', '.PDF']
    #self.create_req_dir()

  @staticmethod
  def safely_create_dir(path):
    if not os.path.exists(path):
      os.mkdir(path)
    return

  # def create_req_dir(self):
  #   idpSettings.safely_create_dir(self.ROOT_INPUT_DIR)
  #   idpSettings.safely_create_dir(self.INVOICE_LOG)
  #   idpSettings.safely_create_dir(self.TABLE_OUTPUT)
  #   return



