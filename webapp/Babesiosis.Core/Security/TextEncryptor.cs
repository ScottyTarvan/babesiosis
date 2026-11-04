using Babesiosis.Core.Assertions;
using Babesiosis.Core.Extensions;
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;

namespace Babesiosis.Core.Security
{
  public static class TextEncryptor
  {
    public static string Encrypt(string textToEncrypt, string privateKey)
    {
      Assertion.True(privateKey.HasValue() && privateKey.Length >= 32, "Private key must be at least 8 characters");

      byte[] iv = new byte[16];
      byte[] array;

      using (Aes aes = Aes.Create())
      {
        aes.Key = Convert.FromBase64String(privateKey);
        aes.GenerateIV();

        ICryptoTransform encryptor = aes.CreateEncryptor(aes.Key, aes.IV);

        using (MemoryStream memoryStream = new MemoryStream())
        {
          using (CryptoStream cryptoStream = new CryptoStream((Stream)memoryStream, encryptor, CryptoStreamMode.Write))
          {
            using (StreamWriter streamWriter = new StreamWriter((Stream)cryptoStream))
            {
              streamWriter.Write(textToEncrypt);
            }

            array = memoryStream.ToArray();
          }
        }
      }

      var encryptedText = Convert.ToBase64String(array);

      return encryptedText;
    }

    public static string Decrypt(string textToDecrypt, string privateKey)
    {
      Assertion.True(privateKey.HasValue() && privateKey.Length >= 32, "Private key must be at least 8 characters");

      string decryptedText = "";

      byte[] buffer = Convert.FromBase64String(textToDecrypt);

      using (Aes aes = Aes.Create())
      {
        aes.Key = Convert.FromBase64String(privateKey);
        aes.GenerateIV();
        ICryptoTransform decryptor = aes.CreateDecryptor(aes.Key, aes.IV);

        using (MemoryStream memoryStream = new MemoryStream(buffer))
        {
          using (CryptoStream cryptoStream = new CryptoStream((Stream)memoryStream, decryptor, CryptoStreamMode.Read))
          {
            using (StreamReader streamReader = new StreamReader((Stream)cryptoStream))
            {
              decryptedText = streamReader.ReadToEnd();
            }
          }
        }
      }

      return decryptedText;
    }
  }
}
