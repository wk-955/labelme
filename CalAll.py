from SpacingAlgo import CalculationBisectionPoints


class CalAll:

    def __init__(self):
        self.shapes = []

    # 106点

    # 瞳孔74和77号点
    def Cal74And77(self):
        # 74
        point53 = self.shapes[53]['points'][0]
        # point54 = self.shapes[54]['points'][0]
        # point57 = self.shapes[57]['points'][0]
        # x = point53[0] + (point54[0]-point53[0])/2
        # y = point53[1] + (point57[1]-point53[1])/2
        point56 = self.shapes[56]['points'][0]
        x = (point53[0] + point56[0]) / 2
        y = (point53[1] + point56[1]) / 2
        self.shapes[74]['points'][0] = [x, y]

        # 77
        point59 = self.shapes[59]['points'][0]
        # point60 = self.shapes[60]['points'][0]
        # point63 = self.shapes[63]['points'][0]
        # x = point59[0] + (point60[0] - point59[0]) / 2
        # y = point59[1] + (point63[1] - point59[1]) / 2
        point62 = self.shapes[62]['points'][0]
        x = (point59[0] + point62[0]) / 2
        y = (point59[1] + point62[1]) / 2
        self.shapes[77]['points'][0] = [x, y]

    # 脸颊
    def CalFace(self):
        face0 = self.shapes[0]['points'][0]
        face5 = self.shapes[5]['points'][0]
        face9 = self.shapes[9]['points'][0]
        face11 = self.shapes[11]['points'][0]
        face12 = self.shapes[12]['points'][0]
        face13 = self.shapes[13]['points'][0]
        face15 = self.shapes[15]['points'][0]
        face16 = self.shapes[16]['points'][0]
        left_face = [face0, face5, face9, face11, face12, face13, face15, face16]
        intervalNum = 16
        c = CalculationBisectionPoints()
        long = c.calculateDistanceSum(left_face)
        c.pointArr = left_face
        c.spacing = long / intervalNum
        c.doCalculate()
        # return c.spacingPoints
        # points = self.Cal(left_face, intervalNum)
        if c.spacingPoints:
            count = 0
            for i in range(1, 16):
                self.shapes[i]["points"][0] = list(c.spacingPoints[count])
                count += 1

        face16 = self.shapes[16]['points'][0]
        face17 = self.shapes[17]['points'][0]
        face19 = self.shapes[19]['points'][0]
        face20 = self.shapes[20]['points'][0]
        face21 = self.shapes[21]['points'][0]
        face23 = self.shapes[23]['points'][0]
        face27 = self.shapes[27]['points'][0]
        face32 = self.shapes[32]['points'][0]
        right_face = [face16, face17, face19, face20, face21, face23, face27, face32]
        # intervalNum = 16
        c = CalculationBisectionPoints()
        long = c.calculateDistanceSum(right_face)
        c.pointArr = right_face
        c.spacing = long / intervalNum
        c.doCalculate()
        # points = self.Cal(right_face, intervalNum)
        if c.spacingPoints:
            count = 0
            for i in range(17, 32):
                self.shapes[i]["points"][0] = list(c.spacingPoints[count])
                count += 1

    # 眉毛
    def Cal106LeftEyebrow(self):
        left_eyebrow33 = self.shapes[33]['points'][0]
        left_eyebrow45 = self.shapes[45 + 106]['points'][0]
        left_eyebrow34 = self.shapes[34]['points'][0]
        left_eyebrow35 = self.shapes[35]['points'][0]
        left_eyebrow36 = self.shapes[36]['points'][0]
        left_eyebrow49 = self.shapes[49 + 106]['points'][0]
        left_eyebrow37 = self.shapes[37]['points'][0]
        upper_eyebrow = [left_eyebrow33, left_eyebrow45, left_eyebrow34, left_eyebrow35, left_eyebrow36,
                         left_eyebrow49, left_eyebrow37]
        intervalNum = 4
        points = self.Cal(upper_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(34, 37):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

        left_eyebrow33 = self.shapes[33]['points'][0]
        left_eyebrow51 = self.shapes[51 + 106]['points'][0]
        left_eyebrow64 = self.shapes[64]['points'][0]
        left_eyebrow65 = self.shapes[65]['points'][0]
        left_eyebrow66 = self.shapes[66]['points'][0]
        left_eyebrow55 = self.shapes[55 + 106]['points'][0]
        left_eyebrow67 = self.shapes[67]['points'][0]
        lower_eyebrow = [left_eyebrow33, left_eyebrow51, left_eyebrow64, left_eyebrow65,
                         left_eyebrow66, left_eyebrow55, left_eyebrow67]
        points = self.Cal(lower_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(64, 67):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

    def Cal106RightEyebrow(self):
        right_eyebrow38 = self.shapes[38]['points'][0]
        right_eyebrow62 = self.shapes[62 + 106]['points'][0]
        right_eyebrow39 = self.shapes[39]['points'][0]
        right_eyebrow40 = self.shapes[40]['points'][0]
        right_eyebrow41 = self.shapes[41]['points'][0]
        right_eyebrow58 = self.shapes[58 + 106]['points'][0]
        right_eyebrow42 = self.shapes[42]['points'][0]
        upper_eyebrow = [right_eyebrow38, right_eyebrow62, right_eyebrow39, right_eyebrow40,
                         right_eyebrow41, right_eyebrow58, right_eyebrow42]
        intervalNum = 4
        points = self.Cal(upper_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(39, 42):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

        right_eyebrow68 = self.shapes[68]['points'][0]
        right_eyebrow68_1 = self.shapes[68 + 106]['points'][0]
        right_eyebrow69 = self.shapes[69]['points'][0]
        right_eyebrow70 = self.shapes[70]['points'][0]
        right_eyebrow71 = self.shapes[71]['points'][0]
        right_eyebrow64 = self.shapes[64 + 106]['points'][0]
        right_eyebrow42 = self.shapes[42]['points'][0]
        lower_eyebrow = [right_eyebrow68, right_eyebrow68_1, right_eyebrow69,
                         right_eyebrow70, right_eyebrow71, right_eyebrow64, right_eyebrow42]
        points = self.Cal(lower_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(69, 72):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

    # 眼睛
    def CalLeftEye(self, ):
        left_eye52 = self.shapes[52]['points'][0]
        left_eye12 = self.shapes[12 + 106]['points'][0]
        left_eye53 = self.shapes[53]['points'][0]
        left_eye72 = self.shapes[72]["points"][0]
        left_eye54 = self.shapes[54]['points'][0]
        left_eye21 = self.shapes[21 + 106]['points'][0]
        left_eye55 = self.shapes[55]['points'][0]
        upper_eye = [left_eye52, left_eye12, left_eye53, left_eye72,
                     left_eye54, left_eye21, left_eye55]
        intervalNum = 4
        points = self.Cal(upper_eye, intervalNum)
        if points:
            self.shapes[53]["points"][0] = list(points[0])
            self.shapes[72]["points"][0] = list(points[1])
            self.shapes[54]["points"][0] = list(points[2])

        left_eye0 = self.shapes[0 + 106]['points'][0]
        left_eye57 = self.shapes[57]['points'][0]
        left_eye73 = self.shapes[73]['points'][0]
        left_eye56 = self.shapes[56]['points'][0]
        left_eye9 = self.shapes[9 + 106]['points'][0]
        lower_eye = [left_eye52, left_eye0, left_eye57, left_eye73,
                     left_eye56, left_eye9, left_eye55]
        intervalNum = 4
        points = self.Cal(lower_eye, intervalNum)
        if points:
            self.shapes[57]["points"][0] = list(points[0])
            self.shapes[73]["points"][0] = list(points[1])
            self.shapes[56]["points"][0] = list(points[2])

    def CalRightEye(self):
        right_eye58 = self.shapes[58]['points'][0]
        right_eye43 = self.shapes[43 + 106]['points'][0]
        right_eye59 = self.shapes[59]['points'][0]
        right_eye75 = self.shapes[75]['points'][0]
        right_eye60 = self.shapes[60]['points'][0]
        right_eye34 = self.shapes[34 + 106]['points'][0]
        right_eye61 = self.shapes[61]['points'][0]
        upper_eye = [right_eye58, right_eye43, right_eye59, right_eye75,
                     right_eye60, right_eye34, right_eye61]
        intervalNum = 4
        points = self.Cal(upper_eye, intervalNum)
        if points:
            self.shapes[59]["points"][0] = list(points[0])
            self.shapes[75]["points"][0] = list(points[1])
            self.shapes[60]["points"][0] = list(points[2])

        right_eye58 = self.shapes[58]['points'][0]
        right_eye31 = self.shapes[31 + 106]['points'][0]
        right_eye63 = self.shapes[63]['points'][0]
        right_eye76 = self.shapes[76]['points'][0]
        right_eye62 = self.shapes[62]['points'][0]
        right_eye22 = self.shapes[22 + 106]['points'][0]
        right_eye61 = self.shapes[61]['points'][0]
        lower_eye = [right_eye58, right_eye31, right_eye63, right_eye76,
                     right_eye62, right_eye22, right_eye61]
        points = self.Cal(lower_eye, intervalNum)
        if points:
            self.shapes[63]["points"][0] = list(points[0])
            self.shapes[76]["points"][0] = list(points[1])
            self.shapes[62]["points"][0] = list(points[2])

    # 计算74 75点
    def CalEyeMid(self):
        line1 = self.shapes[53]['points'][0] + self.shapes[56]['points'][0]
        line2 = self.shapes[54]['points'][0] + self.shapes[57]['points'][0]
        self.shapes[74]['points'][0] = self.CalMidPoints(line1, line2)

        line3 = self.shapes[59]['points'][0] + self.shapes[62]['points'][0]
        line4 = self.shapes[60]['points'][0] + self.shapes[63]['points'][0]
        self.shapes[77]['points'][0] = self.CalMidPoints(line3, line4)

    # 上唇
    def Cal106UpperLip(self):
        L_upper_lip84 = self.shapes[84]['points'][0]
        L_upper_lip71 = self.shapes[71 + 106]['points'][0]
        L_upper_lip85 = self.shapes[85]['points'][0]
        L_upper_lip86 = self.shapes[86]['points'][0]
        L_upper_lip = [L_upper_lip84, L_upper_lip71, L_upper_lip85, L_upper_lip86]
        intervalNum = 2
        points = self.Cal(L_upper_lip, intervalNum)
        if points:
            count = 0
            self.shapes[85]["points"][0] = list(points[count])

        R_upper_lip88 = self.shapes[88]['points'][0]
        R_upper_lip89 = self.shapes[89]['points'][0]
        R_upper_lip85 = self.shapes[85 + 106]['points'][0]
        R_upper_lip90 = self.shapes[90]['points'][0]
        R_upper_lip = [R_upper_lip88, R_upper_lip89, R_upper_lip85, R_upper_lip90]
        intervalNum = 2
        points = self.Cal(R_upper_lip, intervalNum)
        if points:
            count = 0
            self.shapes[89]["points"][0] = list(points[count])

        L_lower_lip84 = self.shapes[84]['points'][0]
        L_lower_lip88 = self.shapes[88 + 106]['points'][0]
        L_lower_lip97 = self.shapes[97]['points'][0]
        L_lower_lip94 = self.shapes[94 + 106]['points'][0]
        L_lower_lip98 = self.shapes[98]['points'][0]
        L_lower_lip = [L_lower_lip84, L_lower_lip88, L_lower_lip97, L_lower_lip94, L_lower_lip98]
        intervalNum = 2
        points = self.Cal(L_lower_lip, intervalNum)
        if points:
            count = 0
            self.shapes[97]["points"][0] = list(points[count])

        R_lower_lip98 = self.shapes[98]['points'][0]
        R_lower_lip96 = self.shapes[96 + 106]['points'][0]
        R_lower_lip99 = self.shapes[99]['points'][0]
        R_lower_lip102 = self.shapes[102 + 106]['points'][0]
        R_lower_lip90 = self.shapes[90]['points'][0]
        R_lower_lip = [R_lower_lip98, R_lower_lip96, R_lower_lip99, R_lower_lip102, R_lower_lip90]
        intervalNum = 2
        points = self.Cal(R_lower_lip, intervalNum)
        if points:
            count = 0
            self.shapes[99]["points"][0] = list(points[count])

    # 下唇
    def Cal106LowerLip(self):
        # 下唇左下
        L_lower_lip84 = self.shapes[84]['points'][0]
        L_lower_lip119 = self.shapes[119 + 106]['points'][0]
        L_lower_lip95 = self.shapes[95]['points'][0]
        L_lower_lip94 = self.shapes[94]['points'][0]
        L_lower_lip125 = self.shapes[125 + 106]['points'][0]
        L_lower_lip93 = self.shapes[93]['points'][0]
        L_lower_lip = [L_lower_lip84, L_lower_lip119, L_lower_lip95,
                       L_lower_lip94, L_lower_lip125, L_lower_lip93]
        intervalNum = 3
        points = self.Cal(L_lower_lip, intervalNum)
        if points:
            count = 0
            for i in range(95, 93, -1):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

        # 下唇右下
        R_lower_lip93 = self.shapes[93]['points'][0]
        R_lower_lip127 = self.shapes[127 + 106]['points'][0]
        R_lower_lip92 = self.shapes[92]['points'][0]
        R_lower_lip91 = self.shapes[91]['points'][0]
        R_lower_lip133 = self.shapes[133 + 106]['points'][0]
        R_lower_lip90 = self.shapes[90]['points'][0]
        R_lower_lip = [R_lower_lip93, R_lower_lip127, R_lower_lip92, R_lower_lip91, R_lower_lip133, R_lower_lip90]
        intervalNum = 3
        points = self.Cal(R_lower_lip, intervalNum)
        if points:
            count = 0
            for i in range(92, 90, -1):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

        # 下唇左上
        L_upper_lip84 = self.shapes[84]['points'][0]
        L_upper_lip104 = self.shapes[104 + 106]['points'][0]
        L_upper_lip103 = self.shapes[103]['points'][0]
        L_upper_lip110 = self.shapes[110 + 106]['points'][0]
        L_upper_lip102 = self.shapes[102]['points'][0]
        L_upper_lip = [L_upper_lip84, L_upper_lip104, L_upper_lip103, L_upper_lip110, L_upper_lip102]

        intervalNum = 2
        points = self.Cal(L_upper_lip, intervalNum)
        if points:
            count = 0
            self.shapes[103]["points"][0] = list(points[count])

        # 下唇右上
        R_upper_lip102 = self.shapes[102]['points'][0]
        R_upper_lip112 = self.shapes[112 + 106]['points'][0]
        R_upper_lip101 = self.shapes[101]['points'][0]
        R_upper_lip118 = self.shapes[118 + 106]['points'][0]
        R_upper_lip90 = self.shapes[90]['points'][0]
        R_upper_lip = [R_upper_lip102, R_upper_lip112, R_upper_lip101, R_upper_lip118, R_upper_lip90]
        intervalNum = 2
        points = self.Cal(R_upper_lip, intervalNum)
        if points:
            count = 0
            self.shapes[101]["points"][0] = list(points[count])

    # 134点
    # 眉毛
    def CalLeftUpperEyebrow(self):
        left_eyebrow33 = self.shapes[33]['points'][0]
        left_eyebrow45 = self.shapes[45 + 106]['points'][0]
        left_eyebrow34 = self.shapes[34]['points'][0]
        left_eyebrow35 = self.shapes[35]['points'][0]
        left_eyebrow36 = self.shapes[36]['points'][0]
        left_eyebrow49 = self.shapes[49 + 106]['points'][0]
        left_eyebrow37 = self.shapes[37]['points'][0]
        upper_eyebrow = [left_eyebrow33, left_eyebrow45, left_eyebrow34, left_eyebrow35, left_eyebrow36,
                         left_eyebrow49, left_eyebrow37]
        intervalNum = 6
        points = self.Cal(upper_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(45, 50):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalLeftLowerEyebrow(self):
        left_eyebrow33 = self.shapes[33]['points'][0]
        left_eyebrow51 = self.shapes[51 + 106]['points'][0]
        left_eyebrow64 = self.shapes[64]['points'][0]
        left_eyebrow65 = self.shapes[65]['points'][0]
        left_eyebrow66 = self.shapes[66]['points'][0]
        left_eyebrow55 = self.shapes[55 + 106]['points'][0]
        left_eyebrow67 = self.shapes[67]['points'][0]
        lower_eyebrow = [left_eyebrow33, left_eyebrow51, left_eyebrow64, left_eyebrow65,
                         left_eyebrow66, left_eyebrow55, left_eyebrow67]
        intervalNum = 6
        points = self.Cal(lower_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(51, 56):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalRightUpperEyebrow(self):
        right_eyebrow38 = self.shapes[38]['points'][0]
        right_eyebrow62 = self.shapes[62 + 106]['points'][0]
        right_eyebrow39 = self.shapes[39]['points'][0]
        right_eyebrow40 = self.shapes[40]['points'][0]
        right_eyebrow41 = self.shapes[41]['points'][0]
        right_eyebrow58 = self.shapes[58 + 106]['points'][0]
        right_eyebrow42 = self.shapes[42]['points'][0]
        upper_eyebrow = [right_eyebrow38, right_eyebrow62, right_eyebrow39, right_eyebrow40,
                         right_eyebrow41, right_eyebrow58, right_eyebrow42]
        intervalNum = 6
        points = self.Cal(upper_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(62, 57, -1):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalRightLowerEyebrow(self):
        right_eyebrow68 = self.shapes[68]['points'][0]
        right_eyebrow68_1 = self.shapes[68 + 106]['points'][0]
        right_eyebrow69 = self.shapes[69]['points'][0]
        right_eyebrow70 = self.shapes[70]['points'][0]
        right_eyebrow71 = self.shapes[71]['points'][0]
        right_eyebrow64 = self.shapes[64 + 106]['points'][0]
        right_eyebrow42 = self.shapes[42]['points'][0]
        lower_eyebrow = [right_eyebrow68, right_eyebrow68_1, right_eyebrow69,
                         right_eyebrow70, right_eyebrow71, right_eyebrow64, right_eyebrow42]
        intervalNum = 6
        points = self.Cal(lower_eyebrow, intervalNum)
        if points:
            count = 0
            for i in range(68, 63, -1):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    # 眼睛
    def CalLeftUpperEye(self, ):
        left_eye52 = self.shapes[52]['points'][0]
        left_eye55 = self.shapes[55]['points'][0]
        left_eye53 = self.shapes[53]['points'][0]
        left_eye72 = self.shapes[72]["points"][0]
        left_eye54 = self.shapes[54]['points'][0]
        upper_eye = [left_eye52, left_eye53, left_eye72, left_eye54, left_eye55]
        intervalNum = 11
        points = self.Cal(upper_eye, intervalNum)
        if points:
            for i in range(118, 128):
                self.shapes[i]["points"][0] = list(points[i - 118])

    def CalLeftLowerEye(self):
        left_eye52 = self.shapes[52]['points'][0]
        left_eye55 = self.shapes[55]['points'][0]
        # 下沿
        left_eye57 = self.shapes[57]['points'][0]
        left_eye73 = self.shapes[73]['points'][0]
        left_eye56 = self.shapes[56]['points'][0]
        lower_eye = [left_eye52, left_eye57, left_eye73, left_eye56, left_eye55]
        intervalNum = 11
        points = self.Cal(lower_eye, intervalNum)
        if points:
            for i in range(106, 116):
                self.shapes[i]["points"][0] = points[i - 106]

    def CalRightUpperEye(self, ):
        right_eye58 = self.shapes[58]['points'][0]
        right_eye59 = self.shapes[59]['points'][0]
        right_eye75 = self.shapes[75]['points'][0]
        right_eye60 = self.shapes[60]['points'][0]
        right_eye61 = self.shapes[61]['points'][0]
        upper_eye = [right_eye58, right_eye59, right_eye75, right_eye60, right_eye61]
        intervalNum = 11
        points = self.Cal(upper_eye, intervalNum)
        if points:
            count = 0
            for i in range(149, 139, -1):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

    def CalRightLowerEye(self, ):
        right_eye58 = self.shapes[58]['points'][0]
        right_eye63 = self.shapes[63]['points'][0]
        right_eye76 = self.shapes[76]['points'][0]
        right_eye62 = self.shapes[62]['points'][0]
        right_eye61 = self.shapes[61]['points'][0]
        lower_eye = [right_eye58, right_eye63, right_eye76, right_eye62, right_eye61]
        intervalNum = 11
        points = self.Cal(lower_eye, intervalNum)
        if points:
            count = 0
            for i in range(137, 127, -1):
                self.shapes[i]["points"][0] = list(points[count])
                count += 1

    # 嘴唇
    def CalUpperLipUpper(self):
        self.CalUULLip()
        self.CalUURLip()

    def CalUpperLipLower(self):
        self.CalULLLip()
        self.CalULRLip()

    def CalLowerLipUpper(self):
        self.CalLULLip()
        self.CalLURLip()

    def CalLowerLipLower(self):
        self.CalLLLLip()
        self.CalLLRLip()

    def CalUULLip(self):
        L_upper_lip84 = self.shapes[84]['points'][0]
        L_upper_lip71 = self.shapes[71 + 106]['points'][0]
        L_upper_lip85 = self.shapes[85]['points'][0]
        L_upper_lip86 = self.shapes[86]['points'][0]
        L_upper_lip = [L_upper_lip84, L_upper_lip71, L_upper_lip85, L_upper_lip86]
        intervalNum = 6
        points = self.Cal(L_upper_lip, intervalNum)
        if points:
            count = 0
            for i in range(71, 76):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1
        self.shapes[77 + 106]["points"][0] = self.CalMid(self.shapes[76 + 106]["points"][0],
                                                         self.shapes[78 + 106]["points"][0])

    def CalUURLip(self):
        R_upper_lip88 = self.shapes[88]['points'][0]
        R_upper_lip89 = self.shapes[89]['points'][0]
        R_upper_lip85 = self.shapes[85 + 106]['points'][0]
        R_upper_lip90 = self.shapes[90]['points'][0]
        R_upper_lip = [R_upper_lip88, R_upper_lip89, R_upper_lip85, R_upper_lip90]
        intervalNum = 6
        points = self.Cal(R_upper_lip, intervalNum)
        if points:
            count = 0
            for i in range(81, 86):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1
        self.shapes[79 + 106]["points"][0] = self.CalMid(self.shapes[78 + 106]["points"][0],
                                                         self.shapes[80 + 106]["points"][0])

    def CalULLLip(self):
        L_lower_lip84 = self.shapes[84]['points'][0]
        L_lower_lip88 = self.shapes[88 + 106]['points'][0]
        L_lower_lip97 = self.shapes[97]['points'][0]
        L_lower_lip94 = self.shapes[94 + 106]['points'][0]
        L_lower_lip98 = self.shapes[98]['points'][0]
        L_lower_lip = [L_lower_lip84, L_lower_lip88, L_lower_lip97, L_lower_lip94, L_lower_lip98]

        intervalNum = 8
        points = self.Cal(L_lower_lip, intervalNum)
        if points:
            count = 0
            for i in range(88, 95):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalULRLip(self):
        R_lower_lip98 = self.shapes[98]['points'][0]
        R_lower_lip96 = self.shapes[96 + 106]['points'][0]
        R_lower_lip99 = self.shapes[99]['points'][0]
        R_lower_lip102 = self.shapes[102 + 106]['points'][0]
        R_lower_lip90 = self.shapes[90]['points'][0]
        R_lower_lip = [R_lower_lip98, R_lower_lip96, R_lower_lip99, R_lower_lip102, R_lower_lip90]

        intervalNum = 8
        points = self.Cal(R_lower_lip, intervalNum)
        if points:
            count = 0
            for i in range(96, 103):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalLULLip(self):
        L_upper_lip84 = self.shapes[84]['points'][0]
        L_upper_lip104 = self.shapes[104 + 106]['points'][0]
        L_upper_lip103 = self.shapes[103]['points'][0]
        L_upper_lip110 = self.shapes[110 + 106]['points'][0]
        L_upper_lip102 = self.shapes[102]['points'][0]
        L_upper_lip = [L_upper_lip84, L_upper_lip104, L_upper_lip103, L_upper_lip110, L_upper_lip102]

        intervalNum = 8
        points = self.Cal(L_upper_lip, intervalNum)
        if points:
            count = 0
            for i in range(104, 111):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalLURLip(self):
        R_upper_lip102 = self.shapes[102]['points'][0]
        R_upper_lip112 = self.shapes[112 + 106]['points'][0]
        R_upper_lip101 = self.shapes[101]['points'][0]
        R_upper_lip118 = self.shapes[118 + 106]['points'][0]
        R_upper_lip90 = self.shapes[90]['points'][0]
        R_upper_lip = [R_upper_lip102, R_upper_lip112, R_upper_lip101, R_upper_lip118, R_upper_lip90]

        intervalNum = 8
        points = self.Cal(R_upper_lip, intervalNum)
        if points:
            count = 0
            for i in range(112, 119):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalLLLLip(self):
        L_lower_lip84 = self.shapes[84]['points'][0]
        L_lower_lip119 = self.shapes[119 + 106]['points'][0]
        L_lower_lip95 = self.shapes[95]['points'][0]
        L_lower_lip94 = self.shapes[94]['points'][0]
        L_lower_lip125 = self.shapes[125 + 106]['points'][0]
        L_lower_lip93 = self.shapes[93]['points'][0]
        L_lower_lip = [L_lower_lip84, L_lower_lip119, L_lower_lip95,
                       L_lower_lip94, L_lower_lip125, L_lower_lip93]

        intervalNum = 8
        points = self.Cal(L_lower_lip, intervalNum)
        if points:
            count = 0
            for i in range(119, 126):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def CalLLRLip(self):
        R_lower_lip93 = self.shapes[93]['points'][0]
        R_lower_lip127 = self.shapes[127 + 106]['points'][0]
        R_lower_lip92 = self.shapes[92]['points'][0]
        R_lower_lip91 = self.shapes[91]['points'][0]
        R_lower_lip133 = self.shapes[133 + 106]['points'][0]
        R_lower_lip90 = self.shapes[90]['points'][0]
        R_lower_lip = [R_lower_lip93, R_lower_lip127, R_lower_lip92, R_lower_lip91, R_lower_lip133, R_lower_lip90]

        intervalNum = 8
        points = self.Cal(R_lower_lip, intervalNum)
        if points:
            count = 0
            for i in range(127, 134):
                self.shapes[i + 106]["points"][0] = list(points[count])
                count += 1

    def Cal(self, points, intervalNum):
        points = [points[0]] + list(sorted(points[1:-1], key=lambda x: x[0])) + [points[-1]]

        c = CalculationBisectionPoints()
        long = c.calculateDistanceSum(points)
        c.pointArr = points
        c.spacing = long / intervalNum
        c.doCalculate()
        return c.spacingPoints

    def CalMid(self, point1, point2):
        x = (point1[0] + point2[0]) / 2
        y = (point1[1] + point2[1]) / 2
        return [x, y]

    def CalMidPoints(self, line1, line2):
        x1, y1, x2, y2 = line1[0], line1[1], line1[2], line1[3]
        x3, y3, x4, y4 = line2[0], line2[1], line2[2], line2[3]

        k1 = (y2 - y1) * 1.0 / (x2 - x1)
        b1 = y1 * 1.0 - x1 * k1 * 1.0
        if (x4 - x3) == 0:
            k2 = None
            b2 = 0
        else:
            k2 = (y4 - y3) * 1.0 / (x4 - x3)
            b2 = y3 * 1.0 - x3 * k2 * 1.0
        if k2 == None:
            x = x3
        else:
            x = (b2 - b1) * 1.0 / (k1 - k2)
        y = k1 * x * 1.0 + b1 * 1.0
        return [x, y]
