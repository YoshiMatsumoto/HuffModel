from huffcalculate import Calculate
import json
import numpy as np
import tqdm


def main():

    calculate = Calculate('100_pop.geojson', 'A_com.geojson', 0.489773)
    (pop, com) = calculate.LoadData()

    #100mメッシュの点を取得
    pop_ptList = [i['geometry']['coordinates'] for i in pop['features']]
    #商業施設座標の取得
    com_ptList = [i['geometry']['coordinates'] for i in com['features']]
    #売場面積の取得
    com_areaList = [i['properties']['売場面積'] for i in com['features']]
    #100mメッシュの人口を取得, -9999を0に変換
    pop_popList = [i['properties']['H27総人口'] for i in pop['features']]
    pop_popList = calculate.CleanList(pop_popList)

    #売り上げを取得
    com_saleList = [i['properties']['年間商品販売額(百万円)'] for i in com['features']]
    #出力用に取得
    #meshcodeの取得
    pop_meshcodeList = [i['properties']['MESHCODE'] for i in pop['features']]
    #keycodeの取得
    pop_keycodeList = [i['properties']['KEYCODE'] for i in pop['features']]

    exportList =[]

    for i in range(1, 20):
        for j in range(1, 20):
            predictList = calculate.PredictSale(pop_ptList, pop_popList, com_ptList, com_areaList, i*0.1, j*0.1)
            mrs = calculate.MRS(predictList, com_saleList)
            exportList.append(mrs)
            print('area:' , i*0.1 , ', dist:' , j*0.1 , ', mrs:' , mrs)
        
    
    export = np.array(exportList)
    np.savetxt('out.csv',export,delimiter=',')

if __name__ == "__main__":
    main()
