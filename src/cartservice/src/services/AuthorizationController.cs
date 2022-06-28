using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;
using dvcsharp_core_api.Models;
using dvcsharp_core_api.Data;

namespace dvcsharp_core_api
{
   [Route("api/[controller]")]
   public class AuthorizationsController : Controller
   {
      private readonly GenericDataContext _context;

      public AuthorizationsController(GenericDataContext context)
      {
         _context = context;
      }

      [HttpPost]
      public IActionResult Post([FromBody] AuthorizationRequest authorizationRequest)
      {
         if(!ModelState.IsValid)
         {
            return BadRequest(ModelState);
         }

         var response = dvcsharp_core_api.Models.User.
            authorizeCreateAccessToken(_context, authorizationRequest);
            
         if(response == null) {
            return Unauthorized();
         }

         return Ok(response);
      }

      [HttpGet("GetTokenSSO")]
      public IActionResult GetTokenSSO()
      {
         var ssoCookieData = HttpContext.Request.Cookies["sso_ctx"];

         if(String.IsNullOrEmpty(ssoCookieData)) {
            return Unauthorized();
         }

         var ssoCookieDecoded = Convert.FromBase64String(ssoCookieData);
         var ssoCookie = JObject.Parse(System.Text.Encoding.UTF8.GetString(ssoCookieDecoded));

         var userId = ssoCookie["auth_user"];
         if(userId == null) {
            return Unauthorized();
         }

         var user = _context.Users.
            Where(b => b.ID == userId.ToObject<int>()).
            FirstOrDefault();

         if(user == null) {
            return NotFound();
         }

         var response = new Models.AuthorizationResponse();
         response.role = user.role;
         response.accessToken = user.createAccessToken();

         return Ok(response);
      }
   }
}