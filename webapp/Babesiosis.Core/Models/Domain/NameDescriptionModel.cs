namespace Babesiosis.Core.Models.Domain
{
  public abstract class NameDescriptionModel : InstanceModel
  {
    public NameDescriptionModel(string name = "", string description = "")
    {
      Name = name;
      Description = description;
    }
    public string Name { get; set; }
    public string Description { get; set; }

    public override string ToString()
    {
      return Name;
    }
  }
}
