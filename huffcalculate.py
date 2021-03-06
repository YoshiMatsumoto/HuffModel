import numpy as np
import json
# import numba
import tqdm


#計算クラス群
class Calculate(object):

    def __init__(self, pathPop, pathCom):
        self.pathPop = pathPop
        self.pathCom = pathCom

    # @numba.jit
    def LoadData(self):
        '''
        データを読み込むメソッド
        '''
        with open(self.pathPop, 'r', encoding="utf-8") as f:
            pop = json.load(f)
        with open(self.pathCom, 'r', encoding="utf-8") as f:
            com = json.load(f)

        return pop, com

    # @numba.jit
    #距離を測定
    def Dist(self, p1, p2, mode):
        '''
        二地点間の距離を求めるメソッド
        ヒュベニの公式から距離を求める（国土地理院でも同様な方法）
        @param p1,p2 緯度経度（度）をリストで持つもの
        @param mode 測地系 true:世界 false:日本
        @return float 距離(m)
        '''

        #度→ラジアンに変更
        radLat1 = np.deg2rad(p1[0])
        radLon1 = np.deg2rad(p1[1])
        radLat2 = np.deg2rad(p2[0])
        radLon2 = np.deg2rad(p2[1])

        #緯度経度差
        radLatDiff = radLat1 - radLat2
        radLonDiff = radLon1 - radLon2

        #平均経度
        radLatAve = (radLat1 + radLat2) / 2

        #測地系の違い
        if mode == True:
            a = 6378137.0
            b = 6356752.314140356
        else:
            a = 6377397.155
            b = 6356078.963

        #第一離心率^2
        e2 = (a*a - b*b) / (a*a)
        #赤道上の子午線曲率半径
        a1e2 = a * (1 - e2)

        sinLat = np.sin(radLatAve)
        W2 = 1.0 - e2 * (sinLat*sinLat)
        #子午線曲率半径M
        M = a1e2 / (np.sqrt(W2)*W2)
        #卯酉線曲率半径
        N = a / np.sqrt(W2)

        t1 = M * radLatDiff
        t2 = N * np.cos(radLatAve) * radLonDiff
        dist = np.sqrt((t1*t1) + (t2*t2))

        return dist

    # @numba.jit
    def oneAttract(self, sareaList, lareaList, distList, sarea, larea, dist):
        '''
        顧客が店舗(dist, area)での確率を求めるメソッド
        参照 http://desktop.arcgis.com/ja/arcmap/10.3/tools/business-analyst-toolbox/how-original-huff-model-works.htm
        @apram distList すべての店舗までの距離のリスト
        @param areaList すべての店舗の売場面積のリスト
        @param area 面積補正係数
        @param dist 距離補正係数
        @return 店舗の魅力度のリスト
        '''
        #すべての店舗の魅力度を計算
        WList = [(np.float_power(isarea, sarea) + np.float_power(ilarea, larea))/np.float_power(idist, dist) for isarea, ilarea, idist in zip(sareaList, lareaList, distList)]
        sigma_WList = np.sum(WList)

        #すべての店舗へ行く確率を計算
        PList = np.array([iW/sigma_WList for iW in WList])
        return PList

    # @numba.jit
    def PredictSale(self, pop_ptList, pop_popList, com_ptList, com_sareaList, sarea, com_lareaList, larea, dist, distHosei):
        '''
        予測値を求めるメソッド
        @param pop_ptList 人口メッシュの緯度経度リスト
        @param pop_popList 人口メッシュの人口リスト
        @param com_ptList 商業施設の緯度経度リスト
        @param com_areaList 商業施設の売り場面積リスト
        @param area,dist 面積補正係数,距離補正係数
        @return predictSale 売上の予測値
        '''
        allpop_popbyList = []
        for j in tqdm.trange(len(pop_ptList)):
            distList = np.array([abs(self.Dist(pop_ptList[j], i, True)) + distHosei for i in com_ptList])
            Pij = self.oneAttract(com_sareaList, com_lareaList, distList, sarea, larea, dist)
            #人口をかける
            pop_popbyList = np.array([kPij*pop_popList[j] for kPij in Pij])
            #二次元配列にする
            allpop_popbyList.append(pop_popbyList)
            pass

        #集客ポテンシャルの算出
        #転置して各店舗ごとを行にする
        allpop_popbyListT = list(map(list, zip(*allpop_popbyList)))
        #行ごとに合計値を出して、店舗ごとを足し合わせる
        predictSale = np.array([sum(i) for i in allpop_popbyListT])

        return predictSale
