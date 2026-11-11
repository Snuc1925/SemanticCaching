# 10_reset: Console: khôi phục dữ liệu demo

172 lời gọi hàm.

```text
▶ auth.current_user   [0.6 ms]   (thread: AnyIO worker thread, dòng 35)
│    in  request = <Request>
│  ▶ auth.decode   [0.5 ms]   (thread: AnyIO worker thread, dòng 23)
│  │    in  token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiZGU1ODRiZGQtOTA3OS00NTQ1LTkwZWQtZmE1MGNjYjAyNzA3Iiwi…(+1219 ký tự)'
│  │    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ auth.console_user   [0.0 ms]   (thread: AnyIO worker thread, dòng 42)
│    in  user = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ main.admin_reset   [818.5 ms]   (thread: AnyIO worker thread, dòng 274)
│    in  body = ResetIn({clear_history: False})
│    in  actor = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│  ▶ main._acl   [24.3 ms]   (thread: AnyIO worker thread, dòng 207)
│  │    out = {realm: 'semcache', roles: [{name: 'customer', description: 'Khách hàng'}, {name: 'employee', description: 'Nhân viên (mọi phòng ban)'}, {name: 'cskh_agent', description: 'Nhân viên chăm sóc khách hàng'}, {name: 'hr', description: 'Nhân sự'}, {name: 'sales', description: 'Kinh doanh / đại lý'}, {name: 'ops_admin', description: 'Vận hành hệ thống, được vào Console'}], policies: [{name: 'p_any_user', type: 'role', roles: <list>}, {name: 'p_employee', type: 'role', roles: <list>}, {name: 'p_cskh', type: 'role', roles: <list>}, {name: 'p_hr', type: 'role', roles: <list>}, {name: 'p_sales', type: 'role', roles: <list>}, {name: 'p_region_north', type: 'regex', claim: 'region', pattern: '^north$'}, …(+1)], collections: {public: {title: 'Tài liệu công khai', policies: <list>}, internal_all: {title: 'Tài liệu nội bộ chung', policies: <list>}, cskh: {title: 'Tài liệu nội bộ CSKH', policies: <list>}, hr_confidential: {title: 'Nhân sự - mật', policies: <list>}, sales_north: {title: 'Kinh doanh miền Bắc', policies: <list>}, sales_south: {title: 'Kinh doanh miền Nam', policies: <list>}}, default_password: 'demo1234', users: [{username: 'khach', name: 'Khách Hàng', roles: <list>}, {username: 'cskh1', name: 'Lan CSKH', roles: <list>}, {username: 'cskh2', name: 'Minh CSKH', roles: <list>}, {username: 'sales_bac', name: 'Hùng Sales Bắc', roles: <list>, attributes: <dict>}, {username: 'sales_nam', name: 'Vy Sales Nam', roles: <list>, attributes: <dict>}, {username: 'hr1', name: 'Hà Nhân Sự', roles: <list>}, …(+1)]}
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [15.1 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'khach'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [15.0 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'khach', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=khach&exact=true>
│  │    out = {id: '25b9ebd4-6b31-4faa-bc66-0a84d42aafff', username: 'khach', firstName: 'Khách', lastName: 'Hàng', email: 'khach@saomai.local', emailVerified: True, createdTimestamp: 1794339204501, enabled: True, totp: False, disableableCredentialTypes: [], …(+3 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [7.3 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = '25b9ebd4-6b31-4faa-bc66-0a84d42aafff'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [7.3 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/25b9ebd4-6b31-4faa-bc66-0a84d42aafff/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/25b9ebd4-6b31-4faa-bc66-0a84d42aafff/role-mappings/realm>
│  │    out = ['default-roles-semcache', 'customer']
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [9.5 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'cskh1'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [9.5 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'cskh1', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=cskh1&exact=true>
│  │    out = {id: '829671b9-5f8b-431d-9b2f-8a31158a3a2d', username: 'cskh1', firstName: 'Lan', lastName: 'CSKH', email: 'cskh1@saomai.local', emailVerified: True, createdTimestamp: 1794339204584, enabled: True, totp: False, disableableCredentialTypes: [], …(+3 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [5.0 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [4.9 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm>
│  │    out = ['employee', 'default-roles-semcache']
│  ▶ iam.keycloak.KeycloakAdmin.set_realm_role   [18.6 ms]   (thread: AnyIO worker thread, dòng 78)
│  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    in  role = 'cskh_agent'
│  │    in  grant = True
│  │  ▶ iam.keycloak.KeycloakAdmin.realm_role   [4.7 ms]   (thread: AnyIO worker thread, dòng 75)
│  │  │    in  name = 'cskh_agent'
│  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [4.7 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │  │    in  method = 'GET'
│  │  │  │    in  path = '/roles/cskh_agent'
│  │  │  │    in  kw = {}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/roles/cskh_agent>
│  │  │    out = {id: 'fce33e7e-8385-4b19-a094-2f378867ecfb', name: 'cskh_agent', description: 'Nhân viên chăm sóc khách hàng', composite: False, clientRole: False, containerId: '36a24d23-b72a-438a-a29d-ea82714c2772', attributes: {}}
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [13.8 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'POST'
│  │  │    in  path = '/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm'
│  │  │    in  kw = {json: [{id: 'fce33e7e-8385-4b19-a094-2f378867ecfb', name: 'cskh_agent'}]}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 204 http://localhost:8080/admin/realms/semcache/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm>
│  │    out = None
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [9.0 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'cskh2'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [8.9 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'cskh2', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=cskh2&exact=true>
│  │    out = {id: '5bc2c24a-35fd-4b7d-a57c-5e41fe659e8a', username: 'cskh2', firstName: 'Minh', lastName: 'CSKH', email: 'cskh2@saomai.local', emailVerified: True, createdTimestamp: 1794339204657, enabled: True, totp: False, disableableCredentialTypes: [], …(+3 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [5.1 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = '5bc2c24a-35fd-4b7d-a57c-5e41fe659e8a'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [5.0 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/5bc2c24a-35fd-4b7d-a57c-5e41fe659e8a/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/5bc2c24a-35fd-4b7d-a57c-5e41fe659e8a/role-mappings/realm>
│  │    out = ['cskh_agent', 'employee', 'default-roles-semcache']
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [10.8 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'sales_bac'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [10.8 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'sales_bac', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=sales_bac&exact=true>
│  │    out = {id: 'eea2aee0-a6a6-4a31-9243-6534436b6068', username: 'sales_bac', firstName: 'Hùng', lastName: 'Sales Bắc', email: 'sales_bac@saomai.local', emailVerified: True, attributes: {region: ['north']}, createdTimestamp: 1794339204705, enabled: True, totp: False, …(+4 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [5.2 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = 'eea2aee0-a6a6-4a31-9243-6534436b6068'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [5.1 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/eea2aee0-a6a6-4a31-9243-6534436b6068/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/eea2aee0-a6a6-4a31-9243-6534436b6068/role-mappings/realm>
│  │    out = ['sales', 'employee', 'default-roles-semcache']
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [10.1 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'sales_nam'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [10.0 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'sales_nam', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=sales_nam&exact=true>
│  │    out = {id: '395ec0ea-23cf-4123-a7f2-9b7376c7b5cb', username: 'sales_nam', firstName: 'Vy', lastName: 'Sales Nam', email: 'sales_nam@saomai.local', emailVerified: True, attributes: {region: ['south']}, createdTimestamp: 1794339204792, enabled: True, totp: False, …(+4 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [5.0 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = '395ec0ea-23cf-4123-a7f2-9b7376c7b5cb'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [4.9 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/395ec0ea-23cf-4123-a7f2-9b7376c7b5cb/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/395ec0ea-23cf-4123-a7f2-9b7376c7b5cb/role-mappings/realm>
│  │    out = ['sales', 'employee', 'default-roles-semcache']
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [11.2 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'hr1'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [11.1 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'hr1', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=hr1&exact=true>
│  │    out = {id: 'be87ef13-5309-4c33-bc9d-bf50cb5647a9', username: 'hr1', firstName: 'Hà', lastName: 'Nhân Sự', email: 'hr1@saomai.local', emailVerified: True, createdTimestamp: 1794339204896, enabled: True, totp: False, disableableCredentialTypes: [], …(+3 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [11.9 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = 'be87ef13-5309-4c33-bc9d-bf50cb5647a9'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [11.8 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/be87ef13-5309-4c33-bc9d-bf50cb5647a9/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/be87ef13-5309-4c33-bc9d-bf50cb5647a9/role-mappings/realm>
│  │    out = ['hr', 'employee', 'default-roles-semcache']
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [12.3 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'admin_ops'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [12.2 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'admin_ops', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=admin_ops&exact=true>
│  │    out = {id: '5b7a9394-f2ca-44a8-acb5-37953e298ad1', username: 'admin_ops', firstName: 'Quản', lastName: 'trị vận hành', email: 'admin_ops@saomai.local', emailVerified: True, createdTimestamp: 1794339204963, enabled: True, totp: False, disableableCredentialTypes: [], …(+3 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.user_realm_roles   [8.3 ms]   (thread: AnyIO worker thread, dòng 72)
│  │    in  user_id = '5b7a9394-f2ca-44a8-acb5-37953e298ad1'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [8.2 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users/5b7a9394-f2ca-44a8-acb5-37953e298ad1/role-mappings/realm'
│  │  │    in  kw = {}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/5b7a9394-f2ca-44a8-acb5-37953e298ad1/role-mappings/realm>
│  │    out = ['ops_admin', 'employee', 'default-roles-semcache']
│  ▶ documents.list_documents   [17.7 ms]   (thread: AnyIO worker thread, dòng 103)
│  │  ▶ db.fetch_all   [3.5 ms]   (thread: AnyIO worker thread, dòng 99)
│  │  │    in  sql = 'SELECT * FROM documents ORDER BY collection, doc_id'
│  │  │    in  params = ()
│  │  │    out = [{doc_id: 'complaint_handling', title: 'Kịch bản xử lý khiếu nại khách hàng', collection: 'cskh', version: 1, updated_at: <datetime>}, {doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', collection: 'cskh', version: 1, updated_at: <datetime>}, {doc_id: 'salary_bonus', title: 'Quy chế lương thưởng (MẬT)', collection: 'hr_confidential', version: 1, updated_at: <datetime>}, {doc_id: 'leave_policy', title: 'Nội quy nghỉ phép', collection: 'internal_all', version: 1, updated_at: <datetime>}, {doc_id: 'membership_faq', title: 'Câu hỏi thường gặp về hạng thành viên', collection: 'public', version: 1, updated_at: <datetime>}, {doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 2, updated_at: <datetime>}, …(+4)]
│  │  ▶ documents.available_versions   [14.0 ms]   (thread: AnyIO worker thread, dòng 30)
│  │  │  ▶ documents.docs_dir   [0.1 ms]   (thread: AnyIO worker thread, dòng 19)
│  │  │  │    out = <PosixPath>
│  │  │  ▶ documents.parse_file   [1.1 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'complaint_handling', title: 'Kịch bản xử lý khiếu nại khách hàng', collection: 'cskh', version: 1}, '# Kịch bản xử lý khiếu nại khách hàng⏎⏎## Thời gian phản hồi⏎Mọi khiếu nại phải được phản hồi lần đầu trong vòng **24 gi…(+494 ký tự)')
│  │  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'dealer_discount_north', title: 'Bảng chiết khấu đại lý miền Bắc', collection: 'sales_north', version: 1}, '# Bảng chiết khấu đại lý miền Bắc⏎⏎## Mức chiết khấu theo cấp đại lý⏎| Cấp đại lý | Doanh số tháng tối thiểu | Chiết khấ…(+327 ký tự)')
│  │  │  ▶ documents.parse_file   [1.8 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'dealer_discount_south', title: 'Bảng chiết khấu đại lý miền Nam', collection: 'sales_south', version: 1}, '# Bảng chiết khấu đại lý miền Nam⏎⏎## Mức chiết khấu theo cấp đại lý⏎| Cấp đại lý | Doanh số tháng tối thiểu | Chiết khấ…(+321 ký tự)')
│  │  │  ▶ documents.parse_file   [0.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'leave_policy', title: 'Nội quy nghỉ phép', collection: 'internal_all', version: 1}, '# Nội quy nghỉ phép⏎⏎## Số ngày phép năm⏎Nhân viên chính thức được **12 ngày phép năm**. Cứ đủ 5 năm làm việc được cộng …(+363 ký tự)')
│  │  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'membership_faq', title: 'Câu hỏi thường gặp về hạng thành viên', collection: 'public', version: 1}, '# Câu hỏi thường gặp về hạng thành viên⏎⏎## Có những hạng thành viên nào?⏎Có 3 hạng: **Thường**, **Bạc** và **VIP**. Hạn…(+457 ký tự)')
│  │  │  ▶ documents.parse_file   [0.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 1}, '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Đ…(+892 ký tự)')
│  │  │  ▶ documents.parse_file   [1.1 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 2}, '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Đ…(+908 ký tự)')
│  │  │  ▶ documents.parse_file   [1.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'salary_bonus', title: 'Quy chế lương thưởng (MẬT)', collection: 'hr_confidential', version: 1}, '# Quy chế lương thưởng (MẬT)⏎⏎## Thưởng Tết⏎Thưởng Tết năm nay bằng **1,7 tháng lương** cơ bản cho nhân viên có thời gia…(+335 ký tự)')
│  │  │  ▶ documents.parse_file   [1.5 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'shipping_policy', title: 'Chính sách giao hàng và lắp đặt', collection: 'public', version: 1}, '# Chính sách giao hàng và lắp đặt⏎⏎## Thời gian giao hàng⏎- Nội thành Hà Nội và TP. Hồ Chí Minh: giao trong **2 giờ** vớ…(+572 ký tự)')
│  │  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', collection: 'cskh', version: 1}, '# Hướng dẫn nội bộ CSKH: Ngoại lệ đổi trả cho khách VIP⏎⏎## Thời hạn đổi trả của khách VIP⏎Khách hàng hạng VIP được đổi …(+541 ký tự)')
│  │  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'warranty_policy', title: 'Chính sách bảo hành và gói bảo hành mở rộng', collection: 'public', version: 1}, '# Chính sách bảo hành và gói bảo hành mở rộng⏎⏎## Bảo hành tiêu chuẩn⏎Tất cả sản phẩm điện máy được bảo hành tiêu chuẩn …(+736 ký tự)')
│  │  │    out = {complaint_handling: {title: 'Kịch bản xử lý khiếu nại khách hàng', collection: 'cskh', versions: [1]}, dealer_discount_north: {title: 'Bảng chiết khấu đại lý miền Bắc', collection: 'sales_north', versions: [1]}, dealer_discount_south: {title: 'Bảng chiết khấu đại lý miền Nam', collection: 'sales_south', versions: [1]}, leave_policy: {title: 'Nội quy nghỉ phép', collection: 'internal_all', versions: [1]}, membership_faq: {title: 'Câu hỏi thường gặp về hạng thành viên', collection: 'public', versions: [1]}, return_policy: {title: 'Chính sách đổi trả hàng', collection: 'public', versions: [1, 2]}, salary_bonus: {title: 'Quy chế lương thưởng (MẬT)', collection: 'hr_confidential', versions: [1]}, shipping_policy: {title: 'Chính sách giao hàng và lắp đặt', collection: 'public', versions: [1]}, vip_return_exception: {title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', collection: 'cskh', versions: [1]}, warranty_policy: {title: 'Chính sách bảo hành và gói bảo hành mở rộng', collection: 'public', versions: [1]}}
│  │    out = [{doc_id: 'complaint_handling', title: 'Kịch bản xử lý khiếu nại khách hàng', collection: 'cskh', versions: [1], current_version: 1, updated_at: '2026-11-10T19:33:30.986039+00:00'}, {doc_id: 'dealer_discount_north', title: 'Bảng chiết khấu đại lý miền Bắc', collection: 'sales_north', versions: [1], current_version: 1, updated_at: '2026-11-10T19:33:31.012496+00:00'}, {doc_id: 'dealer_discount_south', title: 'Bảng chiết khấu đại lý miền Nam', collection: 'sales_south', versions: [1], current_version: 1, updated_at: '2026-11-10T19:33:31.030838+00:00'}, {doc_id: 'leave_policy', title: 'Nội quy nghỉ phép', collection: 'internal_all', versions: [1], current_version: 1, updated_at: '2026-11-10T19:33:31.053447+00:00'}, {doc_id: 'membership_faq', title: 'Câu hỏi thường gặp về hạng thành viên', collection: 'public', versions: [1], current_version: 1, updated_at: '2026-11-10T19:33:31.070515+00:00'}, {doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', versions: [1, 2], current_version: 2, updated_at: '2026-11-11T04:37:58.224386+00:00'}, …(+4)]
│  ▶ documents.ingest   [346.0 ms]   (thread: AnyIO worker thread, dòng 70)
│  │    in  doc_id = 'return_policy'
│  │    in  version = 1
│  │  ▶ documents.file_for   [0.0 ms]   (thread: AnyIO worker thread, dòng 40)
│  │  │    in  doc_id = 'return_policy'
│  │  │    in  version = 1
│  │  │  ▶ documents.docs_dir   [0.0 ms]   (thread: AnyIO worker thread, dòng 19)
│  │  │  │    out = <PosixPath>
│  │  │    out = <PosixPath>
│  │  ▶ documents.parse_file   [0.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 1}, '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Đ…(+892 ký tự)')
│  │  ▶ chunking.chunk_document   [1.0 ms]   (thread: AnyIO worker thread, dòng 107)
│  │  │    in  doc_id = 'return_policy'
│  │  │    in  version = 1
│  │  │    in  collection = 'public'
│  │  │    in  title = 'Chính sách đổi trả hàng'
│  │  │    in  md = '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎## Thời hạn đổi trả⏎Khách h…(+792 ký tự)'
│  │  │    in  max_tokens = 400
│  │  │    in  min_tokens = 80
│  │  │    in  overlap = 50
│  │  │  ▶ chunking._sections   [0.1 ms]   (thread: AnyIO worker thread, dòng 54)
│  │  │  │    in  md = '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎## Thời hạn đổi trả⏎Khách h…(+792 ký tự)'
│  │  │  │    in  title = 'Chính sách đổi trả hàng'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = ''
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = ''
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Khách hàng được đổi trả sản phẩm trong vòng **7 ngày** kể từ ngày nhận hàng. Sau thời hạn này, sản phẩm chỉ được hỗ trợ theo chính sách bảo hành.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn thanh toán tiền mặt được hoàn bằng chuyển khoản.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  │    out = [_Section(path=['Chính sách đổi trả hàng', 'Phạm vi áp dụng'], lines=['Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+25 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Thời hạn đổi trả'], lines=['Khách hàng được đổi trả sản phẩm trong vòng **7 ngày** kể từ ngày nhận hàng. Sau thời hạn này, sản phẩm chỉ được hỗ trợ …(+25 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Điều kiện đổi trả'], lines=['- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.', '- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.', '- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.', '']), _Section(path=['Chính sách đổi trả hàng', 'Hàng điện tử và điện thoại'], lines=['Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâ…(+20 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Hoàn tiền'], lines=['Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn thanh toán tiền mặt được hoàn bằng chuyển…(+7 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Sản phẩm không áp dụng đổi trả'], lines=['Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'])]
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  │    out = 60
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Khách hàng được đổi trả sản phẩm trong vòng **7 ngày** kể từ ngày nhận hàng. Sau thời hạn này, sản phẩm chỉ được hỗ trợ theo chính sách bảo hành.'
│  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.Khách hàng được đổi trả sản phẩm trong vòng **7 ngày** kể từ ngày nhận hàng…(+70 ký tự)'
│  │  │  │    out = 115
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Khách hàng được đổi trả sản phẩm trong vòng **7 ngà…(+94 ký tự)'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Khách hàng được đổi trả sản phẩm trong vòng **7 ngà…(+94 ký tự)'
│  │  │  │    out = 126
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │    out = 91
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  │    out = 61
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn thanh toán tiền mặt được hoàn bằng chuyển khoản.'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn t…(+47 ký tự)'
│  │  │  │    out = 115
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │    out = 121
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Khách hàng được đổi trả sản phẩm trong vòng **7 ngà…(+94 ký tự)'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Khách hàng được đổi trả sản phẩm trong vòng **7 ngà…(+94 ký tự)'
│  │  │  │    out = 126
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Khách hàng được đổi trả sản phẩm trong vòng **7 ngà…(+94 ký tự)'
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │    out = 91
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │    out = 121
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │    in  text = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  │    out = 48
│  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │    out = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │    out = [Chunk(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng', text='Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+194 ký tự)', embed_text='[Chính sách đổi trả hàng > Phạm vi áp dụng]⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điệ…(+238 ký tự)', index=0), Chunk(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả', text='- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎-…(+64 ký tự)', embed_text='[Chính sách đổi trả hàng > Điều kiện đổi trả]⏎- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá …(+110 ký tự)', index=1), Chunk(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại', text='Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâ…(+164 ký tự)', embed_text='[Chính sách đổi trả hàng > Hàng điện tử và điện thoại]⏎Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử…(+219 ký tự)', index=2), Chunk(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả', text='Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".', embed_text='[Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả]⏎Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi…(+35 ký tự)', index=3)]
│  │  ▶ embeddings.embed   [305.5 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  texts = ['[Chính sách đổi trả hàng > Phạm vi áp dụng]⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điệ…(+238 ký tự)', '[Chính sách đổi trả hàng > Điều kiện đổi trả]⏎- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá …(+110 ký tự)', '[Chính sách đổi trả hàng > Hàng điện tử và điện thoại]⏎Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử…(+219 ký tự)', '[Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả]⏎Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi…(+35 ký tự)']
│  │  │    out = ([<vector 1536 số: [-0.0053, 0.0216, -0.0529, …]>, <vector 1536 số: [0.0212, 0.0231, -0.0797, …]>, <vector 1536 số: [-0.0054, 0.0251, -0.0288, …]>, <vector 1536 số: [-0.0192, 0.0438, -0.0110, …]>], 147, False)
│  │  ▶ documents.ensure_collection   [9.1 ms]   (thread: AnyIO worker thread, dòng 44)
│  │  │    out = None
│  │  ▶ db.execute   [3.4 ms]   (thread: AnyIO worker thread, dòng 109)
│  │  │    in  sql = 'INSERT INTO documents(doc_id,title,collection,version,updated_at) VALUES (%s,%s,%s,%s,now())⏎                  ON CONFLICT (doc_id) DO UPDATE SET title=EXCLUDED.title, collection=EXCLUDED.collection,⏎                  ve…(+40 ký tự)'
│  │  │    in  params = ('return_policy', 'Chính sách đổi trả hàng', 'public', 1)
│  │  │    out = None
│  │    out = 4
│  ▶ cache.flush   [279.8 ms]   (thread: AnyIO worker thread, dòng 249)
│  │  ▶ cache.ensure_collection   [261.8 ms]   (thread: AnyIO worker thread, dòng 92)
│  │  │  ▶ embeddings.dim   [1.3 ms]   (thread: AnyIO worker thread, dòng 48)
│  │  │  │  ▶ embeddings.embed_one   [1.3 ms]   (thread: AnyIO worker thread, dòng 43)
│  │  │  │  │    in  text = 'dimension probe'
│  │  │  │  │  ▶ embeddings.embed   [1.2 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │  │  │    in  texts = ['dimension probe']
│  │  │  │  │  │    out = ([<vector 1536 số: [0.0041, 0.0050, -0.0016, …]>], 0, True)
│  │  │  │  │    out = (<vector 1536 số: [0.0041, 0.0050, -0.0016, …]>, 0, True)
│  │  │  │    out = 1536
│  │  │    out = None
│  │    out = 1
│  ▶ access.invalidate_all   [4.8 ms]   (thread: AnyIO worker thread, dòng 66)
│  │    out = 1
│    out = {ok: True}

▶ sync.PermissionSync.poll_once   [44.8 ms]   (thread: permission-sync, dòng 66)
│  ▶ iam.keycloak.KeycloakEventSource.poll   [16.7 ms]   (thread: permission-sync, dòng 156)
│  │  ▶ iam.keycloak.KeycloakAdmin.admin_events   [16.3 ms]   (thread: permission-sync, dòng 112)
│  │  │    in  max_results = 200
│  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [15.7 ms]   (thread: permission-sync, dòng 52)
│  │  │  │    in  method = 'GET'
│  │  │  │    in  path = '/admin-events'
│  │  │  │    in  kw = {params: {max: 200}}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: permission-sync, dòng 39)
│  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMjM3NDlhMGQtMGYxNC00NGI0LThlNjQtODZiODliZGQ5YzZhIiwi…(+1419 ký tự)'
│  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/admin-events?max=200>
│  │  │    out = [{time: 1794371878907, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794371861745, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794370061899, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794370051386, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794369953009, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794369939412, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, …(+50)]
│  │  ▶ iam.keycloak._event_key   [0.0 ms]   (thread: permission-sync, dòng 142)
│  │  │    in  e = {time: 1794371878907, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  │    out = '1794371878907|CREATE|REALM_ROLE_MAPPING|users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm|35052e3dac'
│  │  ▶ iam.keycloak._event_key   [0.0 ms]   (thread: permission-sync, dòng 142)
│  │  │    in  e = {time: 1794371861745, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  │    out = '1794371861745|DELETE|REALM_ROLE_MAPPING|users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm|35052e3dac'
│  │  ▶ iam.keycloak._event_key   [0.0 ms]   (thread: permission-sync, dòng 142)
│  │  │    in  e = {time: 1794371878907, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  │    out = '1794371878907|CREATE|REALM_ROLE_MAPPING|users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm|35052e3dac'
│  │    out = [AccessChangeEvent(occurred_at=<datetime>, kind='role_mapping', summary='CREATE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm)', user_ids=['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], affects_all=False, raw={time: 1794371878907, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: <dict>, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'})]
│  ▶ sync._now   [0.0 ms]   (thread: permission-sync, dòng 23)
│  │    out = <datetime>
│  ▶ access.invalidate   [1.5 ms]   (thread: permission-sync, dòng 62)
│  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    out = True
│  ▶ iam.keycloak.KeycloakAdmin.request   [20.7 ms]   (thread: permission-sync, dòng 52)
│  │    in  method = 'GET'
│  │    in  path = '/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    in  kw = {}
│  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: permission-sync, dòng 39)
│  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMjM3NDlhMGQtMGYxNC00NGI0LThlNjQtODZiODliZGQ5YzZhIiwi…(+1419 ký tự)'
│  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d>
│  ▶ sync._now   [0.0 ms]   (thread: permission-sync, dòng 23)
│  │    out = <datetime>
│  ▶ sync.record_event   [5.5 ms]   (thread: permission-sync, dòng 27)
│  │    in  kind = 'permission_change'
│  │    in  source = 'keycloak'
│  │    in  occurred_at = <datetime>
│  │    in  detected_at = <datetime>
│  │    in  effective_at = <datetime>
│  │    in  summary = 'CREATE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1'
│  │    in  details = {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], usernames: ['cskh1'], signatures_invalidated: 1, operation: 'CREATE', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  ▶ db.fetch_one   [4.5 ms]   (thread: permission-sync, dòng 104)
│  │  │    in  sql = 'INSERT INTO security_events(kind,source,occurred_at,detected_at,effective_at,summary,details)⏎           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *'
│  │  │    in  params = ('permission_change', 'keycloak', <datetime>, <datetime>, <datetime>, 'CREATE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', …(+1))
│  │  │    out = {id: 24, kind: 'permission_change', source: 'keycloak', occurred_at: <datetime>, detected_at: <datetime>, effective_at: <datetime>, summary: 'CREATE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', details: {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], operation: 'CREATE', usernames: ['cskh1'], representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]', signatures_invalidated: 1}}
│  │  ▶ tracing.publish   [0.8 ms]   (thread: permission-sync, dòng 85)
│  │  │    in  kind = 'security'
│  │  │    in  data = {id: 24, kind: 'permission_change', source: 'keycloak', occurred_at: '2026-11-11T04:37:58.907000+00:00', detected_at: '2026-11-11T04:37:59.083887+00:00', effective_at: '2026-11-11T04:37:59.106279+00:00', summary: 'CREATE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', details: {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], operation: 'CREATE', usernames: ['cskh1'], representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]', signatures_invalidated: 1}}
│  │  │    out = None
│  │    out = {id: 24, kind: 'permission_change', source: 'keycloak', occurred_at: '2026-11-11T04:37:58.907000+00:00', detected_at: '2026-11-11T04:37:59.083887+00:00', effective_at: '2026-11-11T04:37:59.106279+00:00', summary: 'CREATE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', details: {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], operation: 'CREATE', usernames: ['cskh1'], representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]', signatures_invalidated: 1}}
│    out = 1

```
