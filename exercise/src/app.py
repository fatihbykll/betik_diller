from src.dosya_islemleri import read_csv, write_json,write_text
from src.processing import stats,build_report , clean_data
def main():
    read_doc="./data/people.csv"
    write_doc="./data/stats.json"
    write_txt="./data/stats_txt.txt"

    #Oku
    rows=read_csv(read_doc)
    rows=clean_data(rows)
    st=stats(rows)

    write_json(write_doc,st)
    write_text(write_txt,build_report(st))
    print("bitti")

if __name__=="__main__":
    main()