from gensim.models import keyedvectors
from sqlalchemy.orm import Session
import db.cruds as query
from typing import *
import numpy as np
import pickle
import pandas as pd


class BookSearcher:
    def __init__(self) -> None:
        """w2v 및 도서 키워드 데이터 로드"""
        self.model = keyedvectors.load_word2vec_format("db/data/update/w2v")
        data = self._read_pkl("db/data/update/data_for_search")
        self.isbn_list = data[0]
        self.book_keyword = data[1]

    def extract_recommand_book_isbn(self, user_search: List[str]) -> dict[str, int]:
        """사용자 검색 결과에 대한 도서 추천 결과를 isbn으로 반환"""
        # extract recommandation keywords
        recommand_keyword = self.model.most_similar(positive=user_search, topn=15)
        np_recommand_keyword = np.array(list(map(lambda x: x[0], recommand_keyword)))

        # calculate recommandation points
        user_point = np.isin(self.book_keyword, np.array(user_search)).sum(axis=1)
        recommand_point = np.isin(self.book_keyword, np_recommand_keyword).sum(axis=1)
        total_point = (user_point * 3) + recommand_point

        top_k_idx = np.argsort(total_point)[::-1][:50]
        return dict(zip(self.isbn_list[top_k_idx], total_point[top_k_idx]))

    def create_book_recommandation_df(self, db: Session, data: Dict) -> pd.DataFrame:
        """
        추천 결과를 바탕으로 도서 데이터 추출
        columns = [publisher, isbn13, bookname, reg_date, class_no, authors, bookImageURL, lib_name]
        """

        isbn_dict = self.extract_recommand_book_isbn(data["user_search"])

        db_result = query.load_lib_name_info(db, list(isbn_dict.keys()), data["selected_lib"])
        lib_book_df = (
            pd.DataFrame(db_result)
            .groupby(by="isbn13")
            .agg(list)
            .applymap(lambda x: " ".join(x))
            .reset_index()
        )

        db_result = query.load_book_info(db, lib_book_df.isbn13.tolist())
        book_info_df = pd.DataFrame(db_result)

        book_df = pd.merge(book_info_df, lib_book_df, on="isbn13").sort_values(
            by="isbn13", key=lambda x: x.map(isbn_dict), ascending=False
        )
        return book_df

    def _read_pkl(self, dir: str):
        with open(dir, "rb") as fp:
            data = pickle.load(fp)
            return data
