# FitLink V1 permissions matrix

Stage 1, 2026-10-03. **Default deny.** Profile type, capability, subscription, verification and relationship membership are independent facts. A User with multiple profiles acts in an explicit context; privileges do not blend across unrelated objects. No professional can read an unrelated athlete's data. UUID guessing, group membership, lead ownership and public profile visits grant no additional access.

## 1. Legend and mandatory predicates

- **Own**: only account holder's data; not another athlete/professional.
- **Scope**: active relationship with explicit training/nutrition responsibility, requested data relevant to that scope, current account permissions and object association. No cross-professional private notes/plans/messages by default.
- **Grant**: Scope plus current athlete Consent for the specific health category/document/photo/purpose. Revoked/expired consent fails even if the relationship remains active.
- **Workspace**: own professional workspace, never all professionals' records.
- **Support**: active fixed `client_support` AssistantMembership plus assigned active client, limited permissions listed below. No sensitive data or private inbox access.
- **Staff**: only named admin capability/purpose, not generic `is_staff`. Sensitive/evidence access requires assigned case or documented exceptional purpose, step-up/MFA and audit. No ordinary plan changes on behalf of a professional.
- **Public**: eligible published allowlisted material only. All roles and anonymous visitors can read public pages; Marketplace flags and publication rules still apply.
- **Archive**: read-only fixed ended-episode service manifest, no future/live data, current purpose-specific archive consent for athlete-derived/sensitive content, and retention/hold restrictions. No assistant archive access. Retained evidence is not ordinary Archive permission.
- **No**: denied. Locked Stage 2 decisions supersede former review defaults.

Every permission also checks account restriction, object state/version, entitlement for advanced actions and feature flag. Object-level checks apply to list/search/count/export/attachments/WebSockets/tasks/AI as well as detail pages. Audited access does not make forbidden access permissible.

## 2. Identity, onboarding, acquisition and public content

| Action | Athlete | Coach | Nutritionist | Both roles | Assistant | Admin |
|---|---|---|---|---|---|---|
| Manage own account/phone/preferences, request export/deletion | Own | Own | Own | Own | Own | Own; Staff privacy workflow for others |
| Create/update athlete baseline/personal health | Own if athlete profile | Own if athlete profile | Own if athlete profile | Own if athlete profile | Own if athlete profile | No routine edits; Staff privacy assistance audited |
| Edit professional profile/setup/branding/locations | No unless professional profile | Workspace | Workspace | Workspace | No | Staff moderation only, not unaudited identity impersonation |
| Upload private credentials/submit verification | No | Workspace | Workspace | Workspace | No | Staff review/decision |
| Approve own verification | No | No | No | No | No | Staff verification, conflict-separated review |
| Publish public profile/package/post | No | Workspace, approved/eligible | Workspace, approved/eligible | Workspace, approved/eligible | No | Staff hide/restrict; no fabricated professional content |
| Read public profiles/packages/prices/posts/reviews | Public | Public | Public | Public | Public | Public |
| See package prices on Marketplace cards | No | No | No | No | No | No public-card exception |
| Favorite/compare max three professionals | Own | Own if athlete profile | Own if athlete profile | Own if athlete profile | Own if athlete profile | No admin override needed |
| Manage packages/discounts/intake questions/capacity | No | Workspace | Workspace | Workspace | No | Staff investigation/config support, not business authorship |
| Submit standard/custom intake and coaching request | Own | Own if athlete profile | Own if athlete profile | Own if athlete profile | Own if athlete profile | No impersonated requests |
| View pending request intake | Own submission | Own workspace request, only submitted/granted fields | Same | Same | No | Staff assigned dispute/verification purpose only |
| Accept/reject request or activate/restart relationship | No acceptance; may withdraw | Workspace, compatible training scope | Workspace, compatible nutrition scope | Workspace, explicit selected scopes | No | No business acceptance; Staff restriction/offboarding intervention audited |
| Join/leave waitlist | Own | Own if athlete profile | Own if athlete profile | Own if athlete profile | Own if athlete profile | Staff investigate only |
| Manage CRM lead/notes/reminders | No | Workspace | Workspace | Workspace | No | Staff assigned investigation, no routine browsing |
| Create referral/invite links | Own | Own | Own | Own | Own general referral; no workspace client invite | Staff disable abusive links |

Unverified professionals retain private workspace/package/intake/relationship management and an owner-only preview. Public page publication, indexing/discovery and Marketplace inclusion are denied until approved verification. Submitted intake is purpose-limited for request evaluation, not longitudinal access. Reject/withdraw removes reviewer access under retention policy.

## 3. Client data, programs, communications and reports

| Action | Athlete | Coach | Nutritionist | Both roles | Assistant | Admin |
|---|---|---|---|---|---|---|
| Read relevant basic profile/normal activity | Own | Scope: training-relevant | Scope: nutrition-relevant | Scope per assignment | Support: basic identity, assigned task/completion status only | Staff assigned case, minimal fields |
| Read structured health/limitations/documents | Own | Grant for training need | Grant for nutrition need | Grant per category/scope | No | Staff justified sensitive case, step-up/audit |
| Add/correct health declarations | Own | No; request athlete correction | No; request athlete correction | No; request athlete correction | No | No routine edits |
| View progress photos/private photo comparisons | Own | Grant for selected photos | Grant for selected photos | Grant for selected photos | No | Staff assigned evidence purpose only |
| Set/revoke health/photo/AI/Mirror/case-study consent | Own | No | No | No | No | Staff can restrict access, never fabricate athlete consent |
| Create platform exercise/food entries | No | Custom workspace entries only | Custom workspace entries only | Custom workspace entries only | No | Staff library curator for platform entries |
| Create workout templates/program/revisions/assignments | Personal workout logs only | Workspace + training Scope | No | Workspace + training Scope | No | No professional plan authorship; Staff platform library only |
| Read professional workout prescription/results | Own assignment/log | Training Scope | No by default; cross-scope detail grant requires approved policy | Training Scope | Support: assigned completion status only, not full prescription/history | Staff assigned case |
| Log/correct actual workout and sync offline | Own | No edits to client actuals | No edits | No edits | No | No routine edits |
| Reschedule own day/select approved substitute | Own valid assignment only | Propose/publish plan revision | No | Training Scope | No | No |
| Submit major program change request | Own | Decide in training Scope | No | Decide in training Scope | No | No |
| Publish/rollback client training plan | No | Training Scope, new revision | No | Training Scope, new revision | No | No; emergency restriction is different from prescribing |
| Create nutrition templates/plans/revisions/assignments | Own actual intake, not professional prescription | No without explicit Nutritionist capability | Workspace + nutrition Scope | Workspace + nutrition Scope | No | No professional plan authorship |
| Read client nutrition plans/detailed intake | Own | No by default; adherence grant does not expose these | Nutrition Scope | Nutrition Scope | No | Staff assigned case |
| View nutrition adherence/discuss non-prescriptive adherence | Own | Active training Scope + explicit nutrition_adherence_read grant; minimized adherence only | Nutrition Scope | Assigned scope + relevant grant | No | Staff assigned case only |
| Confirm/correct AI food image and actual quantities | Own | No for client log | No for client log | No for client log | No | No routine confirmation |
| Record body/daily metrics and personal goals | Own | Read training Scope; scoped goal authoring | Read nutrition Scope; scoped goal authoring | Scope per assignment | No metric detail; task status only | Staff assigned case |
| Build/assign check-in forms, review permitted answers | Own responses only | Training Scope | Nutrition Scope | Scope per form | Support: delivery/completion status only | Staff case only |
| Read/write professional private notes | No | Own Workspace, Scope | Own Workspace, Scope | Own Workspace, Scope | Support: non-sensitive designated workspace notes | Staff assigned case, not routine |
| Read/write direct messages/contextual replies/files | Own conversation participant | Own conversation participant + Scope/Grant for attachment | Same | Same | No private inbox/attachments | Staff reported thread/selected evidence only |
| Author/send broadcasts | No | Workspace active recipients | Workspace active recipients | Workspace active recipients | No | No business broadcasts |
| Manage client tags/groups | No | Workspace | Workspace | Workspace | Support: assigned-client organization only | Staff investigation only |
| Bulk template/check-in/report operation | No | Workspace + per-recipient Scope | Same within nutrition | Per-recipient Scope | No | No professional bulk actions |
| Read unified client timeline | Own sources | Training Scope; filtered sources/Grant | Nutrition Scope; filtered sources/Grant | Union of assigned scopes, not others' private notes | Support: task-status projection only | Staff assigned case, filtered sources |
| Build client/weekly/custom report, export PDF/CSV | Own data export | Workspace + Scope/Grant, advanced entitlement | Same for nutrition | Scoped union | No report builder/export | Staff authorized aggregate metrics or assigned case export |
| View business metrics/manual revenue | No | Workspace | Workspace | Workspace | No | Staff authorized business metrics; revenue labeled unverified |
| Manage appointments/availability/cancellation policy | Own reservations/cancellations | Workspace schedule | Workspace schedule | Workspace schedule | Support: assigned-client scheduling within fixed rules | Staff operational intervention audited |
| Book pre-relationship consultation | Own | Own if athlete profile | Own if athlete profile | Own if athlete profile | Own if athlete profile | No impersonation |
| End/disconnect relationship | Own; immediate | Own Workspace | Own Workspace | Own Workspace | No | Staff safety intervention with reason |
| Read ended relationship archive | Own history under retention | Archive for own delivered training service | Archive for own delivered nutrition service | Archive for own delivered scopes | No | Staff retained case evidence only; hold grants no normal access |

Professional notes shared with the limited assistant must not include health declarations, photo references or copied message contents. Authors mark sensitive private notes restricted to the professional. Unstructured free text can contain accidental sensitive material; restricted-by-default notes and explicit non-sensitive designation are required before Support access. At most assigned-client ordinary notes are exposed; assistant membership alone is insufficient. An athlete export excludes professional internal notes while supplying the athlete's own activity and assigned historical plans.

## 4. Reputation, AI, billing and governance

| Action | Athlete | Coach | Nutritionist | Both roles | Assistant | Admin |
|---|---|---|---|---|---|---|
| Write/edit/delete own verified review | Own, qualifying relationship | Own if athlete profile/eligible | Same | Same | Own if athlete profile/eligible | Staff moderation; revision history review |
| Public response to client review | No unless professional target | Workspace target, one response | Same | Same | No | Staff moderate, not impersonate professional response |
| Draft/publish case study | Consent own subject; no unilateral publication | Workspace + explicit content Consent | Same | Same | No | Staff moderate/hide; cannot replace Consent |
| View AI professional insights | No default; shared-summary feature not assumed | Training Scope + Grant where sensitive + Pro | Nutrition Scope + Grant + Pro | Assigned scopes + Grant + Pro | No | Staff restricted troubleshooting/case evidence, minimized |
| Request/view/approve AI training changes | No approval | Pro + training Scope + explicit diff/base approval | No | Same as Coach | No | No professional approval |
| Request/view/approve AI nutrition changes | No approval | No without Nutritionist capability | Pro + nutrition Scope + explicit diff/base approval | Same as Nutritionist | No | No professional approval |
| Use Mirror/view derived session/share summary | Own, Beta/flag enabled; tier from final feature catalog | Own if athlete; shared client summary only with training Grant | Own if athlete; no client summary default | Own if athlete; shared training summary with Grant | Own if athlete; no workspace client summary | Staff technical aggregate, private session only justified case |
| Purchase Pro/manage own subscription | No need for athlete use | Workspace purchaser | Same | Same | No | Staff price/config/reconciliation, audited |
| Record externally paid coaching revenue | No | Workspace manual entry | Same | Same | No | Staff aggregate/assigned dispute; cannot mark gateway verified |
| Manage assistant memberships/assignments | No | Workspace | Workspace | Workspace | No invite/elevation | Staff revoke abusive access |
| Submit moderation report/dispute/evidence | Own relevant context | Own relevant context | Same | Same | Own relevant context | Staff triage/investigate/resolve |
| View private dispute evidence | Own submitted evidence + explicitly released outcome | Own submitted evidence + bounded party outcome | Same | Same | Own evidence only; no workspace proxy | Assigned dispute Staff with reason/step-up/audit |
| Review edit/delete history | Own current text, no admin history access | Current public/target response only | Same | Same | Public only | Staff review moderation |
| Suspend/hide/verify/configure flags/prices | No | No | No | No | No | Named Staff capabilities; audit all changes |
| Read audit logs, platform metrics | No general log browser | Own normal domain history only | Same | Same | No | Named security/audit or metrics Staff scope |
| Lost-phone recovery decision/apply phone change | Own explicit recovery request; no self-approval | Own request | Own request | Own request | Own request | Authorized recovery Staff after evidence verification/new-phone OTP; audit/history and invalidate old auth |
| Configure retention/apply or release record hold | No | No | No | No | No | Named privacy/security/dispute Staff; purpose/reason/review/expiry; no normal-access bypass |
| Send sensitive content to external AI | Own consent only, not direct provider access | Only designed/reviewed feature + required consent/audit; excluded files denied by default | Same | Same | No | Staff privacy review never substitutes for required user consent |

## 5. Assistant fixed role

V1 has one optional limited role: `client_support`, scoped to a single professional workspace and explicitly assigned active clients. It may see basic client identity, assigned task/completion status, schedule within professional-defined availability, maintain assigned client tags/groups and work with explicitly non-sensitive designated notes. It cannot prescribe/publish/rollback plans, access health/photos/intake answers/detailed metric reports/AI, read private messages/files, send broadcasts, manage CRM/revenue/billing/packages/credentials, accept/end relationships or manage assistants. Professional authorship/approval is never delegated to this role. A dual-role professional's assistant still gets exactly this fixed role.

Maximum two active assistants is an engineering default; Free/Pro eligibility is a remaining feature-catalog item, separate from the closed Pro client limit100. Revocation immediately blocks HTTP/WS/tasks/assignments. Multi-workspace assistants choose context; never combine clients. No assistant grant survives ended relationship/revoked membership.

## 6. Derived artifact and race rules

Reports, timeline, AI, links/broadcasts/search are views of current permissions. Store access version and reauthorize before work/release/download. A prior PDF cannot bypass revoked photo consent. Public case-study consent and sensitive AI consent are independent. External AI defaults deny progress photos, health/identity documents, arbitrary private files and raw Mirror video; a specifically designed reviewed feature plus required explicit consent/audit is necessary for any exception. A generic grant or file attachment is insufficient.

Acceptance/AI approval enforce permissions inside the transaction. Each socket action/dispatch rechecks authorization. Sharing an athlete does not expose another professional's notes/messages/suggestions/plans. Coach adherence read is a narrow separate grant, never editing authority. End stops reports/jobs/messages/new data; Archive permits only previously delivered/finalized manifested records, with current consent redaction and no new exports from live data. Revocation can remove normal/archive visibility while audit/held records remain isolated. Staff has no generic bulk health export.

## 7. Stage 2 policy closure

Publication gate, nutrition authority, narrow archive, staged deletion/holds, Free five/Pro configurable beta 100, AI default exclusions, Mirror Beta/thresholds and manual recovery are locked. Central entitlements apply to every client admission path and Pro operation; Admin limit changes require no deployment. Remaining catalog details, retention periods, evidence standards and optional contest scope are in the risk register; none permits weakening these closed policies.
