using AutoMapper;
using Babesiosis.Core.Api.Auth.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Domain;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Auth.Controllers
{
  public class VerifyCaptchaController
  {
    private readonly IAppSettings _appSettings;
    private readonly IMapper _mapper;
    private readonly IDbContextService _dbContextService;
    private readonly IPasswordEncryptor _passwordEncryptor;
    private readonly ITableStorageService _tableStorageService;

    public VerifyCaptchaController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService,
    IMapper mapper,
    IPasswordEncryptor passwordEncryptor,
    ITableStorageService tableStorageService)
    {
      _appSettings = appSettingsService.GetAppSettings();
      _dbContextService = dbContextService;
      _mapper = mapper;
      _passwordEncryptor = passwordEncryptor;
      _tableStorageService = tableStorageService;
    }

    //Use Website https://www.google.com/recaptcha to create your captcha account
    //Link App by using site key and secret key
    //site key is hardcoded into registration form html template
    //secret key is in system configurations(local or DevOps)
    public async Task<bool> HandleCommand(VerifyCaptchaCommand command)
    {
      using var client = new HttpClient();
      var response = await client.PostAsync("https://www.google.com/recaptcha/api/siteverify",
          new FormUrlEncodedContent(new Dictionary<string, string>
          {
                { "secret", _appSettings.Security.ReCaptchaSecretKey },
                { "response", command.Token }
          }));

      var jsonString = await response.Content.ReadAsStringAsync();
      dynamic data = JObject.Parse(jsonString);
      return (bool)data.success;

    }

  }
}
