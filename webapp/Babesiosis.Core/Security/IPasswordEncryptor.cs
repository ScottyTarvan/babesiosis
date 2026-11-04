namespace Babesiosis.Core.Security
{
  public interface IPasswordEncryptor
  {
    /// <summary>
    /// Encrypt & Hash a piece of text
    /// </summary>
    /// <param name="plainText">The unecrypted text</param>
    /// <param name="salt">The salt to hash the password with</param>
    /// <returns>A encrypted hash</returns>
    public string EncryptAndHashPassword(string plainText, string IV, string salt);

    /// <summary>
    /// Generates a random sequence of 32 bytes
    /// </summary>
    /// <returns>byte array with a length of 32</returns>
    public string GenerateSalt();
  }
}
