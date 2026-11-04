using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace Babesiosis.Core.Security
{
  public class PasswordEncryptor : IPasswordEncryptor
  {
    private const int DerivationIterations = 1000;
    private readonly string _encryptionKey;

    public PasswordEncryptor(string encryptionKey)
    {
      _encryptionKey = encryptionKey;
    }

    public string EncryptAndHashPassword(string password, string IV, string salt)
    {
      using (RijndaelManaged rijndael = new RijndaelManaged())
      {
        rijndael.Key = Convert.FromBase64String(_encryptionKey);
        rijndael.IV = Convert.FromBase64String(IV);

        byte[] encryptedPassword = EncryptStringToBytes(password, rijndael.Key, rijndael.IV);
        var passwordHash = HashPassword(encryptedPassword, Convert.FromBase64String(salt));

        return passwordHash;
      }

    }

    private string HashPassword(byte[] encryptedPassword, byte[] salt)
    {
      var pbkdf2 = new Rfc2898DeriveBytes(encryptedPassword, salt, DerivationIterations);
      byte[] hash = pbkdf2.GetBytes(24);

      StringBuilder sb = new StringBuilder();

      for (int i = 0; i < hash.Length; i++)
      {
        sb.Append(hash[i].ToString("X2"));
      }

      return sb.ToString().ToLower();
    }

    private byte[] EncryptStringToBytes(string plainText, byte[] key, byte[] iv)
    {
      if (plainText == null || plainText.Length <= 0)
      {
        throw new ArgumentNullException("plainText");
      }
      if (key == null || key.Length <= 0)
      {
        throw new ArgumentNullException("key");
      }
      if (iv == null || iv.Length <= 0)
      {
        throw new ArgumentNullException("iv");
      }
      byte[] encrypted;

      using (RijndaelManaged rijAlg = new RijndaelManaged())
      {
        rijAlg.Key = key;
        rijAlg.IV = iv;

        ICryptoTransform encryptor = rijAlg.CreateEncryptor(rijAlg.Key, rijAlg.IV);

        using (MemoryStream msEncrypt = new MemoryStream())
        {
          using (CryptoStream csEncrypt = new CryptoStream(msEncrypt, encryptor, CryptoStreamMode.Write))
          {
            using (StreamWriter swEncrypt = new StreamWriter(csEncrypt))
            {
              swEncrypt.Write(plainText);
            }
            encrypted = msEncrypt.ToArray();
          }
        }
      }

      return encrypted;
    }

    public string GenerateSalt()
    {
      using (RijndaelManaged rijndael = new RijndaelManaged())
      {
        rijndael.GenerateIV();
        var salt = Convert.ToBase64String(rijndael.IV);

        return salt;
      }
    }
  }
}
