from transformers import *
import sys
sys.path.append('.')
import os
from news_data.crawlNews.crawlDantri import crawl_News
import glob
import json
import torch
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
from underthesea import sent_tokenize
# tokenizer= BertTokenizer.from_pretrained("NlpHUST/vibert4news-base-cased")
# bert_model = BertModel.from_pretrained("NlpHUST/vibert4news-base-cased")
# print(bert_model)


class M_Sum():
    def __init__(self):
        
        pretrained = "NlpHUST/vibert4news-base-cased"
        self.pretrained = pretrained
        self.tokenizer = BertTokenizer.from_pretrained(self.pretrained)
        self.bert_model = BertModel.from_pretrained(self.pretrained)
        
    def get_data_url(self, dantri_url):
        # json_folder = "news_data/crawlNews/json_data/"
        # cut = dantri_url.split("/")
        # file_name = cut[-1].replace(".htm", '').replace("-", "_")
        # file_name = str(file_name) + ".json"
        # json_storage = os.path.join(json_folder,file_name)
        # print(json_storage)
        # if not (os.path.exists(json_storage)):
        #     news_ = crawl_News(dantri_url)
        #     # print(news_)
        #     # list_of_files = glob.glob('./news_data/crawlNews/json_data/*.json') # * means all if need specific format then *.csv
        #     # # print(list_of_files)
        #     # latest_json_file = max(list_of_files, key=os.path.getctime)
        #     with open(json_storage,'r', encoding='utf-8') as f:
        #         news_data = json.load(f)
        #     title = news_data['content'][0]['title']
        #     description = news_data['content'][0]['description'].replace('(Dân trí) - ','')
        #     paras = news_data['content'][0]['paras']
        #     # os.remove(json_storage)
        #     return title, description,paras
        # else:
        #     with open(json_storage,'r', encoding='utf-8') as f:
        #         news_data = json.load(f)
        #     title = news_data['content'][0]['title']
        #     description = news_data['content'][0]['description'].replace('(Dân trí) - ','')
        #     paras = news_data['content'][0]['paras']
        #     # os.remove(json_storage)
        #     return title, description,paras
        title, description,paras = crawl_News(url=dantri_url)
        return title, description, paras
            
    def vector_calculator_url(self, dantri_url):
        title, description, paras = self.get_data_url(dantri_url)
        print(title, description, paras)
        title_tok = word_tokenize(title, format="text")
        description_tok = word_tokenize(description, format='text')
        paras_tok = [word_tokenize(para, format='text') for para in paras]
        
        # return title_tok, description_tok, paras_tok, len(paras_tok)
        # centroid vector
        input_id_title = self.tokenizer.encode(title_tok,add_special_tokens = True)
        att_mask_title = [int(token_id > 0) for token_id in input_id_title]
        input_ids_title = torch.tensor([input_id_title])
        att_masks_title = torch.tensor([att_mask_title])
        
        input_id_description = self.tokenizer.encode(description_tok,add_special_tokens = True)
        att_mask_description = [int(token_id > 0) for token_id in input_id_description]
        input_ids_description = torch.tensor([input_id_description])
        att_masks_description = torch.tensor([att_mask_description])
        
        with torch.no_grad():
            features_title = self.bert_model(input_ids_title,att_masks_title)
            features_description = self.bert_model(input_ids_description,att_masks_description)
        t_d = torch.stack((features_title.pooler_output, features_description.pooler_output))
        centroid_doc = torch.mean(t_d, axis=0)
        # print(centroid_doc.shape)
        
        #vector sentences
        n = len(paras)
        sents_vec_dict = {v: k for v, k in enumerate(paras_tok)}    
        for index in range(n) : 
            input_id = self.tokenizer.encode(paras_tok[index],add_special_tokens = True)
            att_mask = [int(token_id > 0) for token_id in input_id]
            input_ids = torch.tensor([input_id])
            att_masks = torch.tensor([att_mask])
            with torch.no_grad():
                features = self.bert_model(input_ids,att_masks)
            sents_vec_dict.update({index:features.pooler_output})
            
        return sents_vec_dict, centroid_doc
    def summary_url(self,dantri_url, auto_selection=True):
        paras = self.get_data_url(dantri_url)[2]
        # print(len(paras))
        # print(paras)
        if auto_selection == False :
            k = 5
        else :
            k = round(len(paras)/ 2 + 1)
        sents_vec_dict, centroid_doc = self.vector_calculator_url(dantri_url)
        cosine_sim = {}
        for key in sents_vec_dict.keys():
            cosine_2vec = cosine_similarity(centroid_doc, sents_vec_dict[key])
            # print(centroid_doc.shape, sents_vec_dict[key].shape)
            cosine_sim.update({key:cosine_2vec})
        # print(cosine_sim)
        final_sim = sorted(cosine_sim.items(), key=lambda x:x[1], reverse=True)
        list_index = dict(final_sim[:k]).keys()
        # print(list_index)
        result = []
        for index in sorted(list_index):
            result.append(paras[index])
        return '\n\n'.join(result)
    def vector_calculator_doc(self, doc):
        doc_tok = [word_tokenize(doc, format='text') for doc in sent_tokenize(doc)]
        n = len(doc_tok)
        sents_vec_dict = {v: k for v, k in enumerate(doc_tok)}    
        for index in range(n) : 
            input_id = self.tokenizer.encode(doc_tok[index],add_special_tokens = True)
            att_mask = [int(token_id > 0) for token_id in input_id]
            input_ids = torch.tensor([input_id])
            att_masks = torch.tensor([att_mask])
            with torch.no_grad():
                features = self.bert_model(input_ids,att_masks)
            sents_vec_dict.update({index:features.pooler_output})
        X = list(sents_vec_dict.values())
        X = torch.stack(X)
        # print(X.shape)
        centroid_doc = torch.mean(X,0)  
        return sents_vec_dict, centroid_doc
    def summary_doc(self, doc, auto_select_sent=True):
        if auto_select_sent == False :
            k = 5
        else :
            k = round(len(doc.split('.'))/ 2 + 1)
        sents_vec_dict, centroid_doc = self.vector_calculator_doc(doc)
        cosine_sim = {}
        for key in sents_vec_dict.keys():
            cosine_2vec = cosine_similarity(centroid_doc, sents_vec_dict[key])
            # print(centroid_doc.shape, sents_vec_dict[key].shape)
            cosine_sim.update({key:cosine_2vec})
        final_sim = sorted(cosine_sim.items(), key=lambda x:x[1], reverse=True)
        list_index = dict(final_sim[:k]).keys()
        result = []
        doc_sents = sent_tokenize(doc)
        for index in sorted(list_index):
            result.append(doc_sents[index])
        mingg = '\n\n'.join(result)
        return mingg

    
# if __name__ == '__main__':    
#     sum = M_Sum()  
  
#     print(sum.get_data_url('https://dantri.com.vn/the-gioi/quan-doi-my-phat-hien-linh-kien-dien-tu-dac-biet-trong-khi-cau-trung-quoc-20230214095227105.htm'))
#     print('-------------------------------')
#     print(sum.get_data_url('https://dantri.com.vn/kinh-doanh/bo-sung-326-trang-tai-lieu-flc-van-no-co-dong-mot-thong-tin-quan-trong-20220508143837505.htm'))   