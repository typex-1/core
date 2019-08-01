struct InitParame {
  1: string L
}


struct ProtocolOne {
  1: string t1,
  2: string t2,
  3: string t3,
  4: string t4,
  5: string t5,
  6: string gamma,
  7: string sz1,
  8: string sz,
  9: string sa,
  10: string sb1,
  11: string sb2,
  12: string sg,
  13: string sh,
  14: string sy,
  15: string M,
  16: string L,
  17: string d,
  18: string u,
  19: string x,
  20: string s1,
  21: string s2,
  22: string v,
  23: string sxi
}

struct ReturnOne {
  1: string zeta1,
  2: string zeta2,
  3: string alpha,
  4: string beta1,
  5: string beta2,
  6: string epsilon,
  7: string e,
  8: string c,
  9: string r,
  10: string roi,
  11: string omega,
  12: string sigma1,
  13: string sigma2,
  14: string delta,
  15: string xiv,
  16: string sxiv,
  17: string szeta1,
  18: string szeta2
}

struct ReturnTwo {
  1: string omdelta
  2: string hashres
}

struct ProtocolTwo {
  1: string omega,
  2: string delta,
  3: string L,
  4: string sg,
  5: string roi,
  6: string sy,
  7: string sigma1,
  8: string sigma2,
  9: string szeta1,
  10: string szeta2,
  11: string sh,
  12: string m
}

struct PublicParame {
  1: string g,
  2: string h,
  3: string sg,
  4: string sh,
  5: string x,
  6: string y,
  7: string gamma,
  8: string xi,
  9: string sy,
  10: string sxi,
  11: string z,
  12: string sz
}

struct IssueParame {
  1: string L,
  2: string sg,
  3: string sh,
  4: string yt,
  5: string gamma,
  6: string sz
}

struct RetIssue {
  1: string zu,
  2: string v,
  3: string u,
  4: string d,
  5: string s1,
  6: string s2,
  7: string t1,
  8: string t2,
  9: string t3,
  10: string t4,
  11: string t5,
  12: string z1,
  13: string z2,
  14: string a,
  15: string b1,
  16: string b2
  17: string szu,
  18: string sz1,
  19: string sz2,
  20: string sa,
  21: string sb1,
  22: string sb2
}

service setup {
  PublicParame init(1: InitParame initParame)
  RetIssue issue(1: IssueParame issueParame)
  ReturnOne execOne(1: ProtocolOne protocolone)
  ReturnTwo execTwo(1: ProtocolTwo protocoltwo)
}