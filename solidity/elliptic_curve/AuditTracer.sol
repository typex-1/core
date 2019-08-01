pragma solidity ^0.4.18;

contract AuditTracer {
    
    uint256 public gx;
    uint256 public gy;
    uint256 public p;
	uint256 public n;
    uint256 public a;
    uint256 public b;
 
    // The address of the account that created this ballot.
    address public tracerCreator;
    mapping (address => uint256) private CredentialTraceTimes;
    mapping (address => uint256) private CredentialTraceResults;
    
    mapping (address => uint256) private IdentityTraceTimes;
    mapping (address => uint256) private IdentityTraceResults;
	
    uint256 public seed = 0;
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
	
	function register_parameter(uint256 _a, uint256 _b, uint256 _p, uint256 _n, uint256 _gx, uint256 _gy) public{ 
		a = _a;
		b = _b;
		p = _p;
		n = _n;
		gx = _gx;
		gy = _gy;
        xt = rand_less_than(_n);
    }
    
    function get_private_key() public view returns(uint256){  
		return xt;
	}
    
    function calculate_public_key() public{  
        (yt_x, yt_y) = multiplyScalar(gx, gy, xt);
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
            (c_x,c_y) = multiplyScalar(xiupsilon_x, xiupsilon_y, xt);
        }
        credential_tracing_log(xiupsilon_x);
    }
    
    // trace the identity
    function identity_calculating(uint256 zeta1_x, uint256 zeta1_y) public{
        if (IdentityTraceTimes[msg.sender] == 0){
            uint256 nxt = inverseMod(xt, n);
            (i_x,i_y) = multiplyScalar(zeta1_x, zeta1_y, nxt);	
        }
        identity_tracing_log(zeta1_x);
    }
    
    function rand_less_than(uint256 upper_bound) private returns(uint256){
        uint256 r = PRNG() % upper_bound;
		return r;
    }
    
    function PRNG() private view returns(uint256) {
        return uint256(uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty,msg.sender,now)))) ;
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

/**
     * @dev Inverse of u in the field of modulo m.
     */
    function inverseMod(uint u, uint m) internal pure
        returns (uint)
    {
        if (u == 0 || u == m || m == 0)
            return 0;
        if (u > m)
            u = u % m;

        int t1;
        int t2 = 1;
        uint r1 = m;
        uint r2 = u;
        uint q;

        while (r2 != 0) {
            q = r1 / r2;
            (t1, t2, r1, r2) = (t2, t1 - int(q) * t2, r2, r1 - q * r2);
        }

        if (t1 < 0)
            return (m - uint(-t1));

        return uint(t1);
    }

    /**
     * @dev Transform affine coordinates into projective coordinates.
     */
    function toProjectivePoint(uint x0, uint y0) public view
        returns (uint[3] memory P)
    {
        P[2] = addmod(0, 1, p);
        P[0] = mulmod(x0, P[2], p);
        P[1] = mulmod(y0, P[2], p);
    }

    /**
     * @dev Add two points in affine coordinates and return projective point.
     */
    function addAndReturnProjectivePoint(uint x1, uint y1, uint x2, uint y2) public view
        returns (uint[3] memory P)
    {
        uint x;
        uint y;
        (x, y) = add(x1, y1, x2, y2);
        P = toProjectivePoint(x, y);
    }

    /**
     * @dev Transform from projective to affine coordinates.
     */
    function toAffinePoint(uint x0, uint y0, uint z0) public view
        returns (uint x1, uint y1)
    {
        uint z0Inv;
        z0Inv = inverseMod(z0, p);
        x1 = mulmod(x0, z0Inv, p);
        y1 = mulmod(y0, z0Inv, p);
    }

    /**
     * @dev Return the zero curve in projective coordinates.
     */
    function zeroProj() public view
        returns (uint x, uint y, uint z)
    {
        return (0, 1, 0);
    }

    /**
     * @dev Return the zero curve in affine coordinates.
     */
    function zeroAffine() public pure
        returns (uint x, uint y)
    {
        return (0, 0);
    }

    /**
     * @dev Check if the curve is the zero curve.
     */
    function isZeroCurve(uint x0, uint y0) public view
        returns (bool isZero)
    {
        if(x0 == 0 && y0 == 0) {
            return true;
        }
        return false;
    }

    /**
     * @dev Check if a point in affine coordinates is on the curve.
     */
    function isOnCurve(uint x, uint y) public view
        returns (bool)
    {
        if (0 == x || x == p || 0 == y || y == p) {
            return false;
        }

        uint LHS = mulmod(y, y, p); // y^2
        uint RHS = mulmod(mulmod(x, x, p), x, p); // x^3

        if (a != 0) {
            RHS = addmod(RHS, mulmod(x, a, p), p); // x^3 + a*x
        }
        if (b != 0) {
            RHS = addmod(RHS, b, p); // x^3 + a*x + b
        }

        return LHS == RHS;
    }

    /**
     * @dev Double an elliptic curve point in projective coordinates. See
     * https://www.nayuki.io/page/elliptic-curve-point-addition-in-projective-coordinates
     */
    function twiceProj(uint x0, uint y0, uint z0) public view
        returns (uint x1, uint y1, uint z1)
    {
        uint t;
        uint u;
        uint v;
        uint w;

        if(isZeroCurve(x0, y0)) {
            return zeroProj();
        }

        u = mulmod(y0, z0, p);
        u = mulmod(u, 2, p);

        v = mulmod(u, x0, p);
        v = mulmod(v, y0, p);
        v = mulmod(v, 2, p);

        x0 = mulmod(x0, x0, p);
        t = mulmod(x0, 3, p);

        z0 = mulmod(z0, z0, p);
        z0 = mulmod(z0, a, p);
        t = addmod(t, z0, p);

        w = mulmod(t, t, p);
        x0 = mulmod(2, v, p);
        w = addmod(w, p-x0, p);

        x0 = addmod(v, p-w, p);
        x0 = mulmod(t, x0, p);
        y0 = mulmod(y0, u, p);
        y0 = mulmod(y0, y0, p);
        y0 = mulmod(2, y0, p);
        y1 = addmod(x0, p-y0, p);

        x1 = mulmod(u, w, p);

        z1 = mulmod(u, u, p);
        z1 = mulmod(z1, u, p);
    }

    /**
     * @dev Add two elliptic curve points in projective coordinates. See
     * https://www.nayuki.io/page/elliptic-curve-point-addition-in-projective-coordinates
     */
    function addProj(uint x0, uint y0, uint z0, uint x1, uint y1, uint z1) public view
        returns (uint x2, uint y2, uint z2)
    {
        uint t0;
        uint t1;
        uint u0;
        uint u1;

        if (isZeroCurve(x0, y0)) {
            return (x1, y1, z1);
        }
        else if (isZeroCurve(x1, y1)) {
            return (x0, y0, z0);
        }

        t0 = mulmod(y0, z1, p);
        t1 = mulmod(y1, z0, p);

        u0 = mulmod(x0, z1, p);
        u1 = mulmod(x1, z0, p);

        if (u0 == u1) {
            if (t0 == t1) {
                return twiceProj(x0, y0, z0);
            }
            else {
                return zeroProj();
            }
        }

        (x2, y2, z2) = addProj2(mulmod(z0, z1, p), u0, u1, t1, t0);
    }

    /**
     * @dev Helper function that splits addProj to avoid too many local variables.
     */
    function addProj2(uint v, uint u0, uint u1, uint t1, uint t0) private view
        returns (uint x2, uint y2, uint z2)
    {
        uint u;
        uint u2;
        uint u3;
        uint w;
        uint t;

        t = addmod(t0, p-t1, p);
        u = addmod(u0, p-u1, p);
        u2 = mulmod(u, u, p);

        w = mulmod(t, t, p);
        w = mulmod(w, v, p);
        u1 = addmod(u1, u0, p);
        u1 = mulmod(u1, u2, p);
        w = addmod(w, p-u1, p);

        x2 = mulmod(u, w, p);

        u3 = mulmod(u2, u, p);
        u0 = mulmod(u0, u2, p);
        u0 = addmod(u0, p-w, p);
        t = mulmod(t, u0, p);
        t0 = mulmod(t0, u3, p);

        y2 = addmod(t, p-t0, p);

        z2 = mulmod(u3, v, p);
    }

    /**
     * @dev Add two elliptic curve points in affine coordinates.
     */
    function add(uint x0, uint y0, uint x1, uint y1) public view
        returns (uint, uint)
    {
        uint z0;

        (x0, y0, z0) = addProj(x0, y0, 1, x1, y1, 1);

        return toAffinePoint(x0, y0, z0);
    }

    /**
     * @dev Double an elliptic curve point in affine coordinates.
     */
    function twice(uint x0, uint y0) public view
        returns (uint, uint)
    {
        uint z0;

        (x0, y0, z0) = twiceProj(x0, y0, 1);

        return toAffinePoint(x0, y0, z0);
    }

    /**
     * @dev Multiply an elliptic curve point by a 2 power base (i.e., (2^exp)*P)).
     */
    function multiplyPowerBase2(uint x0, uint y0, uint exp) public view
        returns (uint, uint)
    {
        uint base2X = x0;
        uint base2Y = y0;
        uint base2Z = 1;

        for(uint i = 0; i < exp; i++) {
            (base2X, base2Y, base2Z) = twiceProj(base2X, base2Y, base2Z);
        }

        return toAffinePoint(base2X, base2Y, base2Z);
    }

    /**
     * @dev Multiply an elliptic curve point by a scalar.
     */
    function multiplyScalar(uint x0, uint y0, uint scalar) public view
        returns (uint x1, uint y1)
    {
        if(scalar == 0) {
            return zeroAffine();
        }
        else if (scalar == 1) {
            return (x0, y0);
        }
        else if (scalar == 2) {
            return twice(x0, y0);
        }

        uint base2X = x0;
        uint base2Y = y0;
        uint base2Z = 1;
        uint z1 = 1;
        x1 = x0;
        y1 = y0;

        if(scalar%2 == 0) {
            x1 = y1 = 0;
        }

        scalar = scalar >> 1;

        while(scalar > 0) {
            (base2X, base2Y, base2Z) = twiceProj(base2X, base2Y, base2Z);

            if(scalar%2 == 1) {
                (x1, y1, z1) = addProj(base2X, base2Y, base2Z, x1, y1, z1);
            }

            scalar = scalar >> 1;
        }

        return toAffinePoint(x1, y1, z1);
    }

    /**
     * @dev Multiply the curve's generator point by a scalar.
     */
    function multipleGeneratorByScalar(uint scalar) public view
        returns (uint, uint)
    {
        return multiplyScalar(gx, gy, scalar);
    }
}
