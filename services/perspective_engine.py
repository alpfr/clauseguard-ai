"""
ClauseGuard AI - Perspective-Aware Negotiation Agent Engine
Adapts risk scoring, severity classification, counter-proposals, and negotiation email scripts
based on the commercial role:
- 'vendor': Service Provider, Contractor, Agency, SaaS Vendor, Freelancer
- 'buyer': Client, Customer, Employer, Enterprise Procurement
- 'balanced': Neutral Commercial Arbitrator / Mutual Standards
"""

from typing import Dict, Any, List


POSTURE_METADATA = {
    "vendor": {
        "id": "vendor",
        "posture": "vendor",
        "title": "Service Provider / Vendor",
        "description": "Protects revenue, payment timelines, background IP, and limits commercial exposure.",
        "icon": "🛡️",
        "focus": "Protecting Service Providers & Contractors",
        "primary_goals": "Capped liability, Net-15/30 payment, retaining pre-existing tools, mutual indemnification."
    },
    "buyer": {
        "id": "buyer",
        "posture": "buyer",
        "title": "Enterprise Buyer / Client",
        "description": "Protects business operations, deliverables IP ownership, supplier accountability, and termination flexibility.",
        "icon": "🏢",
        "focus": "Protecting Corporate Purchasers & IP Rights",
        "primary_goals": "Full deliverables IP transfer, vendor indemnification, right to terminate for convenience, service level warranties."
    },
    "balanced": {
        "id": "balanced",
        "posture": "balanced",
        "title": "Balanced / Commercial Standard",
        "description": "Enforces strict mutual parity, symmetrical liabilities, and industry-standard commercial balance.",
        "icon": "⚖️",
        "focus": "Objective Commercial Baseline Standards",
        "primary_goals": "Equal rights, bilateral confidentiality, mutual indemnification, balanced cure periods."
    }
}


# Perspective adaptation rules for each finding category
# Dict key: finding_id or rule category prefix
PERSPECTIVE_ADAPTATIONS = {
    "indemnity-uncapped": {
        "vendor": {
            "severity": "critical",
            "title": "Uncapped & Asymmetrical Indemnification (Vendor Risk)",
            "explanation": "You are agreeing to defend and indemnify the Client against unlimited commercial, legal, and consequential claims without any financial cap or mutual protection.",
            "counter_proposal": "Replace with mutual indemnification capped at total fees paid under this Agreement in the prior 12 months, strictly limited to third-party direct claims arising from gross negligence or willful misconduct.",
            "script": "Our corporate risk policy and errors & omissions insurance require mutual indemnification capped at total contract fees paid over the preceding 12 months. We have redlined this section to establish market-standard mutual protection limited to direct third-party damages."
        },
        "buyer": {
            "severity": "warning",
            "title": "Vendor Indemnification Scope Review",
            "explanation": "Ensure that the vendor's indemnity broadly covers intellectual property infringement, data breach, and gross negligence without unduly narrow carve-outs.",
            "counter_proposal": "Vendor shall defend and indemnify Client, its officers, and affiliates against any third-party claims arising from IP infringement, data breach, or breach of confidentiality without financial limitation.",
            "script": "As the enterprise customer receiving services and deliverables, our policy requires uncapped supplier indemnification for third-party intellectual property infringement and confidential data breaches to protect our business operations."
        },
        "balanced": {
            "severity": "high",
            "title": "Asymmetrical Indemnification",
            "explanation": "Indemnification is one-sided rather than mutual.",
            "counter_proposal": "Make indemnification strictly mutual, capped at fees paid, with standard exceptions for willful misconduct and confidentiality breaches.",
            "script": "We propose standard mutual indemnification where each party indemnifies the other for their own breach of confidentiality and willful misconduct, subject to agreed liability limits."
        }
    },
    "liability-cap-nominal": {
        "vendor": {
            "severity": "warning",
            "title": "Nominal Liability Limitation",
            "explanation": "A strict liability cap is generally protective for vendors, provided it applies mutually and does not carve out vendor indemnity while leaving client uncapped.",
            "counter_proposal": "Ensure liability is mutually capped at total fees paid by Client in the prior 12 months, applying equally to both parties.",
            "script": "We agree with establishing a clear aggregate liability ceiling, and propose tying this to total contract fees paid over the preceding 12 months to reflect the commercial value of the engagement."
        },
        "buyer": {
            "severity": "critical",
            "title": "Hostile Vendor Liability Cap (Buyer Risk)",
            "explanation": "The vendor is attempting to limit its total financial liability to a trivial amount (e.g. $100 or 1 month of fees), leaving you with no effective legal recourse in the event of gross breach, data loss, or non-delivery.",
            "counter_proposal": "Vendor's liability shall not be limited for breaches of confidentiality, data protection, gross negligence, or indemnification obligations, with a general cap set to not less than 2x total contract value.",
            "script": "A nominal cap of this size leaves our company with virtually no remedy if deliverables fail or confidentiality is compromised. We propose setting the liability cap to at least 2x the annual contract value, with standard super-cap carveouts for IP and data privacy breaches."
        },
        "balanced": {
            "severity": "critical",
            "title": "Severe One-Sided Liability Cap",
            "explanation": "One party has an aggressive liability cap while the other bears open-ended exposure.",
            "counter_proposal": "Establish symmetrical mutual liability cap equal to total fees paid or payable in the 12 months preceding the claim.",
            "script": "We propose a balanced mutual aggregate liability cap equal to 12 months of contract value, providing predictable and fair boundaries for both organizations."
        }
    },
    "ip-broad-assignment": {
        "vendor": {
            "severity": "critical",
            "title": "Overreaching Pre-Existing IP & Tool Assignment (Vendor Risk)",
            "explanation": "This clause transfers ownership of your pre-existing background technology, developer frameworks, methodologies, and proprietary toolkits to the Client.",
            "counter_proposal": "Client owns specific bespoke deliverables created under a Statement of Work upon full payment. Contractor retains all pre-existing tools, libraries, codebases, and general methodologies, granting Client a non-exclusive license to use them with deliverables.",
            "script": "While Client will own all bespoke end deliverables upon receipt of full payment, our business relies on pre-existing development frameworks and background tools that we cannot assign. We have inserted standard language preserving our background IP while granting you an irrevocable license to use it."
        },
        "buyer": {
            "severity": "favorable",
            "title": "Full Intellectual Property Assignment (Buyer Protection)",
            "explanation": "This clause firmly secures complete proprietary ownership of all works, code, and inventions developed under this contract for your company.",
            "counter_proposal": "Maintain full assignment of all custom deliverables and ensure vendor warrants that no third-party open-source components compromise proprietary ownership.",
            "script": "As the commissioning party funding development, full proprietary assignment of all deliverables, code, and designs is a standard requirement for our capital assets and investors."
        },
        "balanced": {
            "severity": "high",
            "title": "Background IP Distinction Needed",
            "explanation": "Fails to distinguish between custom work product and background vendor assets.",
            "counter_proposal": "Explicitly split IP into: (1) Work Product (assigned to Client upon payment), and (2) Background IP (retained by Vendor with perpetual usage license).",
            "script": "We suggest standard commercial IP language: bespoke deliverables transfer to the buyer upon payment, while vendor retains background methodologies subject to a perpetual client usage license."
        }
    },
    "termination-convenience": {
        "vendor": {
            "severity": "high",
            "title": "Unilateral Client Termination on Short Notice (Vendor Risk)",
            "explanation": "Client can cancel without cause on minimal notice, potentially leaving you unpaid for committed resources, pipeline investments, or completed milestones.",
            "counter_proposal": "Client may terminate for convenience upon at least 30 days prior written notice, subject to immediate payment for all work performed, non-cancelable commitments, and a pro-rata wind-down fee.",
            "script": "Due to dedicated staffing and scheduling commitments, we require 30 days prior written notice for convenience termination, along with compensation for all approved work and non-cancelable expenses incurred through the termination date."
        },
        "buyer": {
            "severity": "favorable",
            "title": "Client Termination Flexibility (Buyer Protection)",
            "explanation": "Allows your organization to cancel this vendor engagement swiftly if requirements shift, budget changes, or performance is unsatisfactory.",
            "counter_proposal": "Maintain client termination for convenience upon 14 to 30 days notice with no penalty fees.",
            "script": "Operational agility requires our company to maintain the ability to ramp down third-party consulting agreements on 14–30 days notice without penalty."
        },
        "balanced": {
            "severity": "warning",
            "title": "Asymmetrical Termination Rights",
            "explanation": "One party has termination convenience while the other is locked in.",
            "counter_proposal": "Grant mutual termination for convenience on 30 days written notice with payment for work performed.",
            "script": "We propose mutual termination rights for convenience on 30 days written notice, ensuring fair flexibility for both parties."
        }
    },
    "payment-net-long": {
        "vendor": {
            "severity": "critical",
            "title": "Extended Net 90/120 Cashflow Delay (Vendor Risk)",
            "explanation": "Net 90 or 120 days forces your business to act as an interest-free bank for the Client, creating severe working capital and payroll drag.",
            "counter_proposal": "Invoices shall be payable Net 30 days from receipt. Late payments shall accrue interest at 1.5% per month or the statutory maximum.",
            "script": "Our standard payment terms across all enterprise clients are Net 30 days. We cannot accommodate Net 90/120 terms due to ongoing payroll and vendor commitments. We have updated this to Net 30 with standard late payment interest."
        },
        "buyer": {
            "severity": "favorable",
            "title": "Extended Working Capital Payment Terms (Buyer Protection)",
            "explanation": "Net 60 to 90 days allows your treasury and finance departments to optimize corporate cashflow and verify deliverables before disbursement.",
            "counter_proposal": "Maintain Net 60 days from receipt of a correct, undisputed invoice following formal sign-off.",
            "script": "Our corporate accounting cycle and enterprise payment disbursement runs on a Net 60 schedule for all external consulting vendors."
        },
        "balanced": {
            "severity": "warning",
            "title": "Unfavorable Payment Timeline",
            "explanation": "Payment timeline deviates from commercial standard.",
            "counter_proposal": "Align to commercial standard of Net 30 days with 10-day invoice dispute cure window.",
            "script": "We recommend the commercial standard of Net 30 days, which balances predictable vendor cash flow with adequate client accounting review time."
        }
    },
    "restrictive-noncompete": {
        "vendor": {
            "severity": "critical",
            "title": "Multi-Year Anti-Competitive Restraint (Vendor Risk)",
            "explanation": "A worldwide non-compete prohibits you from serving other clients in your primary industry, threatening your ongoing business viability.",
            "counter_proposal": "Strike out the non-compete clause entirely. Replace with customer and employee non-solicitation strictly limited to active personnel during the term plus 6 months.",
            "script": "As an independent contractor and services agency, non-compete clauses are commercially incompatible with our business model and legally unenforceable in many jurisdictions. We have struck this clause and replaced it with standard non-solicitation."
        },
        "buyer": {
            "severity": "warning",
            "title": "Vendor Non-Compete Enforceability Review",
            "explanation": "Broad non-competes against independent contractors frequently fail legal enforceability tests in court. Focus instead on bulletproof confidentiality and non-solicitation.",
            "counter_proposal": "Protect core interests through airtight trade secret confidentiality and a narrowly tailored 12-month non-solicitation of direct competitive accounts.",
            "script": "To ensure maximum legal enforceability under applicable state law, we have focused our covenant on strict protection of proprietary trade secrets, customer relationships, and key personnel."
        },
        "balanced": {
            "severity": "high",
            "title": "Overly Restrictive Non-Compete",
            "explanation": "Restrictive covenants exceed reasonable geographic or temporal scope.",
            "counter_proposal": "Limit covenants to non-solicitation of active personnel for 12 months with no restriction on general commercial trade.",
            "script": "We propose narrowing this covenant to a 12-month non-solicitation of active employees, which protects legitimate business interests while respecting standard freedom of trade."
        }
    }
}


def get_posture_metadata(posture: str) -> Dict[str, Any]:
    """Retrieve metadata for a given perspective posture."""
    key = posture.lower() if posture else "vendor"
    return POSTURE_METADATA.get(key, POSTURE_METADATA["vendor"])


def apply_perspective(findings: List[Dict[str, Any]], posture: str = "vendor") -> List[Dict[str, Any]]:
    """
    Enrich and adapt a list of findings according to the selected commercial posture:
    - Adjusts severity levels (e.g. flipping vendor-hostile clauses to favorable for buyers).
    - Customizes counter-proposal language.
    - Attaches a copy-pasteable negotiation email script.
    """
    posture_key = (posture or "vendor").lower()
    if posture_key not in ("vendor", "buyer", "balanced"):
        posture_key = "vendor"

    adapted_findings: List[Dict[str, Any]] = []

    for f in findings:
        item = dict(f)
        finding_id = item.get("id", "")

        # Look up adaptation
        adaptation = None
        if finding_id in PERSPECTIVE_ADAPTATIONS:
            adaptation = PERSPECTIVE_ADAPTATIONS[finding_id].get(posture_key)
        else:
            # Fallback matching by category
            cat = item.get("category", "").lower()
            if "indemn" in cat:
                adaptation = PERSPECTIVE_ADAPTATIONS["indemnity-uncapped"].get(posture_key)
            elif "liabilit" in cat:
                adaptation = PERSPECTIVE_ADAPTATIONS["liability-cap-nominal"].get(posture_key)
            elif "intellectual" in cat or "ip" in cat:
                adaptation = PERSPECTIVE_ADAPTATIONS["ip-broad-assignment"].get(posture_key)
            elif "terminat" in cat:
                adaptation = PERSPECTIVE_ADAPTATIONS["termination-convenience"].get(posture_key)
            elif "payment" in cat:
                adaptation = PERSPECTIVE_ADAPTATIONS["payment-net-long"].get(posture_key)
            elif "non-compete" in cat or "restrictive" in cat:
                adaptation = PERSPECTIVE_ADAPTATIONS["restrictive-noncompete"].get(posture_key)

        if adaptation:
            item["severity"] = adaptation.get("severity", item.get("severity"))
            item["title"] = adaptation.get("title", item.get("title"))
            item["explanation"] = adaptation.get("explanation", item.get("explanation"))
            item["counter_proposal"] = adaptation.get("counter_proposal", item.get("counter_proposal"))
            item["negotiation_script"] = adaptation.get("script", "")
        else:
            # Generic script fallback based on posture
            if posture_key == "vendor":
                item["negotiation_script"] = f"We have reviewed the language regarding {item.get('title', 'this provision')} and proposed redline adjustments to ensure reasonable liability boundaries and standard commercial reciprocity."
            elif posture_key == "buyer":
                item["negotiation_script"] = f"As the commissioning organization, we require {item.get('title', 'this provision')} to be clarified to safeguard our company's business assets, deliverables, and operational continuity."
            else:
                item["negotiation_script"] = f"We recommend revising {item.get('title', 'this clause')} to reflect standard bilateral parity between the parties."

        item["posture_applied"] = posture_key
        adapted_findings.append(item)

    return adapted_findings


def recalculate_score_for_posture(findings: List[Dict[str, Any]], posture: str = "vendor") -> Dict[str, Any]:
    """
    Recalculate 0-100 risk score and grade based on the perspective-adjusted findings.
    In Buyer mode, terms favoring the buyer reduce the overall risk score,
    while in Vendor mode, contractor-hostile terms increase the risk score.
    """
    score = 15  # baseline nominal risk
    crit_count = 0
    high_count = 0
    warn_count = 0
    favorable_count = 0

    for f in findings:
        sev = f.get("severity", "warning").lower()
        if sev == "critical":
            score += 35
            crit_count += 1
        elif sev == "high":
            score += 20
            high_count += 1
        elif sev == "warning":
            score += 10
            warn_count += 1
        elif sev == "favorable":
            score = max(5, score - 10)
            favorable_count += 1

    score = min(100, max(5, score))

    if score >= 75:
        grade = "Critical Risk"
        badge_color = "red"
        if posture == "vendor":
            rec = "Do NOT sign in current form. Substantial contractor exposure regarding uncapped liabilities, delayed cashflow, or IP forfeiture."
        elif posture == "buyer":
            rec = "Do NOT execute. Significant supplier disclaimers, lack of warranties, or inadequate deliverables IP transfer."
        else:
            rec = "Severe contractual imbalance detected. Extensive bilateral redlining required prior to signing."
    elif score >= 45:
        grade = "Moderate / High Risk"
        badge_color = "amber"
        if posture == "vendor":
            rec = "Contains unfavorable vendor terms. Redline payment deadlines and restrictive covenants before signing."
        elif posture == "buyer":
            rec = "Adequate structure with specific gaps in supplier accountability and termination remedies. Propose targeted amendments."
        else:
            rec = "Contains moderate one-sided clauses. Standard commercial redlining recommended."
    else:
        grade = "Low Risk / Favorable"
        badge_color = "green"
        if posture == "buyer":
            rec = "Highly favorable contract for the Client/Buyer. Secure terms, strong IP ownership, and operational flexibility."
        elif posture == "vendor":
            rec = "Well-balanced agreement with reasonable supplier protections and standard commercial terms."
        else:
            rec = "Balanced agreement adhering to mutual commercial standards."

    return {
        "score": score,
        "grade": grade,
        "badge_color": badge_color,
        "recommendation": rec,
        "metrics": {
            "critical_flags": crit_count,
            "high_flags": high_count,
            "warnings": warn_count,
            "favorable_clauses": favorable_count,
            "total_audited": len(findings)
        }
    }
