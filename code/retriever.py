# import your libraries here

class Retriever:

    def get_result(self,state,parsed):

        result = {
            'biz_name':'',
            'biz_location':'',
            'category':'',
            'comment':''
        }

        # based on state (which contains food, cuisine, location) get 1 business that matches

        result['biz_name'] = ''
        result['biz_location'] = ''
        result['category'] = ''

        # based on jaccard, levenshtein or cosine similarity get 1 comment

        result['comment'] = ''

        return result
