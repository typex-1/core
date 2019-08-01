pragma solidity ^0.4.18;

contract AuditTracer {
    
    uint256 public gx;
    uint256 public gy;
    uint256 public p;
    uint256 public a;
    uint256 public b;
 
    // The address of the account that created this ballot.
    address public tracerCreator;
    mapping (address => uint256) private CredentialTraceTimes;
    mapping (address => uint256) private CredentialTraceResults;
    
    mapping (address => uint256) private IdentityTraceTimes;
    mapping (address => uint256) private IdentityTraceResults;
	
    uint256 public index = 0;
    uint256 public xt;
    
    uint256 public yt_x;
    uint256 public yt_y;
    
    uint256 public c_x;
    uint256 public c_y;
    
    uint256 public i_x;
    uint256 public i_y;
    
    constructor() public {
        tracerCreator = msg.sender;
    }
 
    event trace_log(
        string information,
        address indexed sender,
        uint256 timestamp,
        uint256 calltimes,
        uint256 obj
    );
    
    function credential_tracing_log(uint256 obj) internal {
         emit trace_log("credential_tracing_log", msg.sender, now, CredentialTraceTimes[msg.sender], obj);
    }
    
    function identity_tracing_log(uint256 obj) internal {
         emit trace_log("credential_tracing_log", msg.sender, now, IdentityTraceTimes[msg.sender], obj);
    }
	
	function register_parameter(uint256 _a, uint256 _b, uint256 _p, uint256 _gx, uint256 _gy) public{ 
		a = _a;
		b = _b;
		p = _p;
		gx = _gx;
		gy = _gy;
        xt = rand_less_than(_p);
    }
    
    function get_private_key() public view returns(uint256){  
		return xt;
	}
    
    function calculate_public_key() public{  
        (yt_x, yt_y) = ecmul(gx, gy, xt);
	}
	
	function get_public_key() public view returns(uint256 , uint256 ){  
		return (yt_x, yt_y);
	}
	
	function credential_tracing() public returns(uint256,uint256){
	        CredentialTraceTimes[msg.sender] += 1;
	    return (c_x,c_y);
	}
	
	function identity_tracing() public returns(uint256,uint256){
	        CredentialTraceTimes[msg.sender] += 1;
	     return (i_x,i_y);
	}

	// trace the credential
    function credential_calculating(uint256 xiupsilon_x, uint256 xiupsilon_y) public{
	    if (CredentialTraceTimes[msg.sender] == 0){
            (c_x,c_y) = ecmul(xiupsilon_x, xiupsilon_y, xt);
        }
        credential_tracing_log(xiupsilon_x);
    }
    
    // trace the identity
    function identity_calculating(uint256 zeta1_x, uint256 zeta1_y) public{
        if (IdentityTraceTimes[msg.sender] == 0){
            uint256 nxt = quick_power(xt, p - 2, p);
            (i_x,i_y) = ecmul(zeta1_x, zeta1_y, nxt);
        }
        identity_tracing_log(zeta1_x);
    }
    
    function rand_less_than(uint256 upper_bound) private returns(uint256){
        index = index + 1;
        uint256 r = PRNG(index) % upper_bound;
		return r;
    }
    
    function PRNG(uint256 seed) private view returns(uint256) {
        return uint256(uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty,msg.sender,now,seed)))) ;
    }

    function quick_power(uint256 al, uint256 bl, uint256 m) private pure returns(uint256){
      uint256 result = 1;
      for(uint256 count = 1; count <= bl; count*=2){
          if(bl & count != 0){
              result = mulmod(result, al, m);
          }
          al = mulmod(al, al, m);
      }
      return result;
    }

    function _jAdd(
        uint256 x1, uint256 z1,
        uint256 x2, uint256 z2)
        internal 
        view
        returns(uint256 x3, uint256 z3)
    {
        (x3, z3) = (
            addmod(
                mulmod(z2, x1, p),
                mulmod(x2, z1, p),
                p
            ),
            mulmod(z1, z2, p)
        );
    }

    function _jSub(
        uint256 x1, uint256 z1,
        uint256 x2, uint256 z2)
        internal 
        view
        returns(uint256 x3, uint256 z3)
    {
        (x3, z3) = (
            addmod(
                mulmod(z2, x1, p),
                mulmod(p - x2, z1, p),
                p
            ),
            mulmod(z1, z2, p)
        );
    }

    function _jMul(
        uint256 x1, uint256 z1,
        uint256 x2, uint256 z2)
        public 
        view
        returns(uint256 x3, uint256 z3)
    {
        (x3, z3) = (
            mulmod(x1, x2, p),
            mulmod(z1, z2, p)
        );
    }

    function _jDiv(
        uint256 x1, uint256 z1,
        uint256 x2, uint256 z2) 
        internal 
        view
        returns(uint256 x3, uint256 z3)
    {
        (x3, z3) = (
            mulmod(x1, z2, p),
            mulmod(z1, x2, p)
        );
    }

    function _inverse(uint256 val) internal view
        returns(uint256 invVal)
    {
        uint256 t = 0;
        uint256 newT = 1;
        uint256 r = p;
        uint256 newR = val;
        uint256 qi;
        while (newR != 0) {
            qi = r / newR;

            (t, newT) = (newT, addmod(t, (p - mulmod(qi, newT, p)), p));
            (r, newR) = (newR, r - qi * newR );
        }

        return t;
    }

    function _ecAdd(
        uint256 x1, uint256 y1, uint256 z1,
        uint256 x2, uint256 y2, uint256 z2) 
        internal 
        view
        returns(uint256 x3, uint256 y3, uint256 z3)
    {
        uint256 lx;
        uint256 lz;
        uint256 da;
        uint256 db;

        if (x1 == 0 && y1 == 0) {
            return (x2, y2, z2);
        }

        if (x2 == 0 && y2 == 0) {
            return (x1, y1, z1);
        }

        if (x1 == x2 && y1 == y2) {
            (lx, lz) = _jMul(x1, z1, x1, z1);
            (lx, lz) = _jMul(lx, lz, 3, 1);
            (lx, lz) = _jAdd(lx, lz, a, 1);

            (da,db) = _jMul(y1, z1, 2, 1);
        } else {
            (lx, lz) = _jSub(y2, z2, y1, z1);
            (da, db) = _jSub(x2, z2, x1, z1);
        }

        (lx, lz) = _jDiv(lx, lz, da, db);

        (x3, da) = _jMul(lx, lz, lx, lz);
        (x3, da) = _jSub(x3, da, x1, z1);
        (x3, da) = _jSub(x3, da, x2, z2);

        (y3, db) = _jSub(x1, z1, x3, da);
        (y3, db) = _jMul(y3, db, lx, lz);
        (y3, db) = _jSub(y3, db, y1, z1);

        if (da != db) {
            x3 = mulmod(x3, db, p);
            y3 = mulmod(y3, da, p);
            z3 = mulmod(da, db, p);
        } else {
            z3 = da;
        }
    }

    function _ecDouble(uint256 x1, uint256 y1, uint256 z1) internal view
        returns(uint256 x3, uint256 y3, uint256 z3)
    {
        (x3, y3, z3) = _ecAdd(x1, y1, z1, x1, y1, z1);
    }

    function _ecMul(uint256 d, uint256 x1, uint256 y1, uint256 z1) internal view
        returns(uint256 x3, uint256 y3, uint256 z3)
    {
        uint256 remaining = d;
        uint256 px = x1;
        uint256 py = y1;
        uint256 pz = z1;
        uint256 acx = 0;
        uint256 acy = 0;
        uint256 acz = 1;

        if (d == 0) {
            return (0, 0, 1);
        }

        while (remaining != 0) {
            if ((remaining & 1) != 0) {
                (acx,acy,acz) = _ecAdd(acx, acy, acz, px, py, pz);
            }
            remaining = remaining / 2;
            (px, py, pz) = _ecDouble(px, py, pz);
        }

        (x3, y3, z3) = (acx, acy, acz);
    }

    function ecadd(
        uint256 x1, uint256 y1,
        uint256 x2, uint256 y2)
        internal
        view
        returns(uint256 x3, uint256 y3)
    {
        uint256 z;
        (x3, y3, z) = _ecAdd(x1, y1, 1, x2, y2, 1);
        z = _inverse(z);
        x3 = mulmod(x3, z, p);
        y3 = mulmod(y3, z, p);
    }

    function ecmul(uint256 x1, uint256 y1, uint256 scalar) public view
        returns(uint256 x2, uint256 y2)
    {
        uint256 z;
        (x2, y2, z) = _ecMul(scalar, x1, y1, 1);
        z = _inverse(z);
        x2 = mulmod(x2, z, p);
        y2 = mulmod(y2, z, p);
    }

}
