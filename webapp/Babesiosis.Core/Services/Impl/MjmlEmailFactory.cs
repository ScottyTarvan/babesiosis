using Babesiosis.Core.Configurations;
using Babesiosis.Core.Exceptions;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Email;
using Babesiosis.Core.Models.Teams;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  internal class MjmlEmailFactory : IEmailFactory
    {
        private readonly string _header;
        private readonly string _footer;
        private readonly string _noReply;
        private readonly IAppSettings _appSettings;

        public MjmlEmailFactory(IAppSettingsService appSettingsService)
        {
            _appSettings = appSettingsService.GetAppSettings();
            _noReply = "system@Babesiosis.co.za";

            _header = $@"
            <mjml>
              <mj-body background-color='#ffffff'>
              <mj-section background-color='#009EF7' padding-bottom='0px' padding-top='0px'>
                <mj-column vertical-align='top' width='100%'>
     	           <mj-text align='right' color='white' font-size='20px' font-family='open Sans Helvetica, Arial, sans-serif'>F-IT</mj-text>
                </mj-column >
             </mj-section>";

                  _footer = $@"
              </mj-body>
            </mjml>";
        }

        #region IEmailFactory Implementation
        #region Admin Email Implementations

        public async Task<Email> CreateForgotPasswordEmailAsync(User user, string token)
        {
            string link = $"{_appSettings.WebApp.Url}auth/reset-password?token={token}";
            var sb = new StringBuilder();

            sb.Append(_header);

            sb.Append(@$"
            <mj-section padding-bottom='10px' padding-top='10px'>
              <mj-column vertical-align='middle' width='100%'>
               <mj-text align='left' padding-left='25px' padding-right='25px'>
                 Dear {user.FirstName} {user.LastName},
               </mj-text>
                <mj-text align='left' padding-left='25px' padding-right='25px'>
                  We have recently received a request to change the password attached to this email-address. 
                  If this was you please click on the link below to continue the password reset process.
               </mj-text>
               <mj-text align='left' padding-left='25px' padding-right='25px'>
                          <a href='{link}'>
                    Reset Password
                  </a>
               </mj-text>
               <mj-text align='left' padding-left='25px' padding-right='25px'>
                  Thanks and Kind Regards, 
               </mj-text> 
               <mj-text align='left' padding-left='25px' padding-right='25px'>
                  The F-IT Team.
               </mj-text>  
              </mj-column>                                  
            </mj-section>");

            sb.Append(_footer);

            var emailBody = await ConvertMjmlToHtmlAsync(sb.ToString());

            var email = new Email
            {
                Body = emailBody,
                CreatedDate = DateTime.UtcNow,
                FromAddress = _noReply,
                Subject = $"Forgotten Password Recovery",
                ToAddress = user.Email
            };

            return email;
        }

        #endregion

        #endregion

        internal async Task<string> ConvertMjmlToHtmlAsync(string mjml)
        {
            var req = new MjmlApiRequest { Mjml = mjml };

            var postBody = new StringContent(
              JsonConvert.SerializeObject(req),
              Encoding.UTF8,
              "application/json");

            using var client = new HttpClient();

            var httpRequestMessage = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri($"{_appSettings.MjmlApi.ApiUrl}/render"),
                Content = postBody
            };

            httpRequestMessage.Headers.Authorization = new AuthenticationHeaderValue(
              "Basic",
              Convert.ToBase64String(Encoding.UTF8.GetBytes($"{_appSettings.MjmlApi.ApplicationId}:{_appSettings.MjmlApi.ApiKey}")));

            var response = await client.SendAsync(httpRequestMessage);
            var responseObject = JsonConvert.DeserializeObject<MjmlApiResponse>(await response.Content.ReadAsStringAsync());

            if (responseObject.Errors.Any())
            {
                throw new AggregateException(responseObject.Errors.Select(e => new MjmlTranspileException(e.Message)));
            }

            return responseObject.Html;
        }

        private class MjmlApiRequest
        {
            public string Mjml { get; set; }
        }

        private class MjmlApiResponse
        {
            public string Mjml { get; set; }
            public string Html { get; set; }
            public string MjmlVersion { get; set; }
            public IEnumerable<MjmlError> Errors { get; set; }
        }

        private class MjmlError
        {
            public string Message { get; set; }
            public string TagName { get; set; }
            public string FormattedMessage { get; set; }
            public string LineNumber { get; set; }
        }
    }
}
