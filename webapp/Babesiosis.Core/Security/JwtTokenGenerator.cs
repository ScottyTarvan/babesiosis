using Babesiosis.Core.Extensions;
using Microsoft.IdentityModel.Tokens;
using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace Babesiosis.Core.Security
{
  public class JwtTokenGenerator : IJwtTokenGenerator
  {
    private readonly string _audience;
    private readonly string _issuer;
    private readonly string _securityKey;
    private readonly TimeSpan _jwtTExpiryTimeSpan;

    public JwtTokenGenerator(string securityKey, string audience, string issuer, TimeSpan jwttExpiryTimeSpan)
    {
      _securityKey = securityKey;
      _audience = audience;
      _issuer = issuer;
      _jwtTExpiryTimeSpan = jwttExpiryTimeSpan;
    }

    public string CreateToken(Guid userId, TimeSpan timeTillExpires)
    {
      var signingKey = CreateSigningKey(_securityKey);

      var credentials = new SigningCredentials(
        signingKey,
        SecurityAlgorithms.HmacSha256Signature,
        SecurityAlgorithms.Sha256Digest);

      var identity = new ClaimsIdentity(
        new List<Claim>()
        {
          new Claim(ClaimTypes.Actor, userId.ToB())
        }, "Custom");

      var descriptor = new SecurityTokenDescriptor
      {
        Audience = _audience,
        Issuer = _issuer,
        Subject = identity,
        SigningCredentials = credentials,
        Expires = DateTime.UtcNow.Add(timeTillExpires)
      };

      var handler = new JwtSecurityTokenHandler();
      var token = handler.CreateToken(descriptor);
      return handler.WriteToken(token);
    }


    public bool ValidateToken(string token)
    {
      try
      {
        var (securityToken, claimsPrincipal) = GetSecurityToken(token);
        return DateTime.UtcNow < securityToken.ValidTo;
      }
      catch
      {
        return false;
      }
    }

    public Guid GetUserId(string token)
    {
      var (_, claimsPrincipal) = GetSecurityToken(token);
      return Guid.Parse(claimsPrincipal.FindFirst(ClaimTypes.Actor).Value);
    }

    public (SecurityToken, ClaimsPrincipal) GetSecurityToken(string token)
    {
      var signingKey = CreateSigningKey(_securityKey);

      var tokenValidationParameters = new TokenValidationParameters
      {
        ValidAudiences = new string[]
      {
        _audience
      },
        ValidIssuers = new string[]
      {
        _issuer
      },
        IssuerSigningKey = signingKey
      };

      var tokenHandler = new JwtSecurityTokenHandler();

      var principal = tokenHandler.ValidateToken(
        token,
        tokenValidationParameters,
        out SecurityToken securityToken);

      return (securityToken, principal);
    }

    private SymmetricSecurityKey CreateSigningKey(string securityKey) => new SymmetricSecurityKey(Encoding.UTF8.GetBytes(securityKey));
  }
}
