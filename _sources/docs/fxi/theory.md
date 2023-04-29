[Full slides of the course](../Slides/fxi_theory_practice/fxi_theory_practice.pdf)

<!-- https://cheatography.com/xaon/cheat-sheets/emacs-markdown-mode/  -->
# Conceptual Framework

## The Trilemma

`````{admonition} The Mundell Trilemma
:class: warning
The choice of the monetary framework and the goals of the central bank is constrained by the **Mundell Trilemma**, that states that countries can only achieve two out of the three objectives:
  * Independent monetary policy: for instance, determining the interest rate to achieve domestic objectives, such as controlling inflation 
  * Open capital account: capital flows can freely move in and out the country 
  * Fixed exchange rate: the local currency is pegged to an anchor, for instance, the US dollar or the 
`````

Most advanced economies have abandonned the fixed exchange rate objective after the collapse of the Bretton Woods system, and are therefore pursuing independent monetary objectives (inflation targeting or, in the past, money-base targeting) under an open capital account.

Diagram of the Mundell Trilemma with some countries illustration
![Trilemma](../Slides/fxi_theory_practice/img/Trilemma.PNG)
*Source: Lafarguette*

Typically, countries trying to "round the corners of the trilemma", i.e. trying to achieve the three objectives simultaneously, will at a point face severe exchange rate/capital flows pressures if the fundamentals are not aligned. After burning their FX reserves to maintain a misaligned exchange rate level with open capital flows and independent monetary policy, countries will ultimately have to give up either open capital account or the peg. 

This situation occurred in South-East Asia at the end of the 1990s (the 1997 Asian Financial Crisis). At the time:
  * Most East-Asia countries in the 90s were *de facto* pegged to the USD 
  * Free mobility of capital (except in China)
  * Independent monetary policy with a high domestic interest rate to attract foreign investors
    * Countries were growing fast, foreign capital supplemented the lack of domestic savings
    * FX peg + high interest rate were generating a positive carry without FX risk for investors. Consequently, it fueled **hot money**
    * Huge credit boom: at the time, South-East Asia was receiving **half** of the world total capital flows to EM by the time 

These factors generated a **credit bubble** on over-leveraged economies, fueled by hot money

Hence, when the bubble bursted (first in Thailand), investors ran, triggering capital outflows and weakening currencies
  * Due to insufficient foreign reserves, countries were forced to devaluate, as FX interventions were not possible
  * The huge FX mismatch on banks and corporates balance sheets started a crisis, which was amplified by the interest rate hikes motivated to fight depreciation...


Exchange rate dynamics of South-East Asian Countries during the 1997 Asian Financial Crisis
![AFC FX Crash](../Slides/fxi_theory_practice/img/afc_fx_crash.PNG)
*Source: Nikkei Asia and Refinitiv*


Evolution of the GDP of South-East Asian Countries during the 1997 Asian Financial Crisis
![AFC GDP Crash](../Slides/fxi_theory_practice/img/afc_gdp_crash.png)
*Source: Mark Roser, Our World in Data*

    
## Goals and Intermediate Objectives

`````{admonition} Definition: FX Interventions
:class: definition
Any official sale or purchase of foreign assets against domestic assets **in the foreign exchange market** (onshore or offshore)
`````
* FX Interventions are usually carried-out by the central bank, but can sometimes be under the responsibility of the Ministry of Finances, such as in Japan ([link](https://www.mof.go.jp/english/policy/international_policy/reference/feio/index.html))

Typically, the central banking literature distinguishes between goals and objectives:

`````{admonition} Central Bank Goal
:class: important
Ultimate purpose of the FX intervention. Should be consistent with the monetary framework of the central bank
````` 
*For instance, a FX intervention goal for the central bank could be about preserving financial stability*


`````{admonition} Intermediate Objectives
:class: important
How to reach the goals via the central bank's operational framework
````` 
*For instance, mitigating FX daily volatility via open-market interventions*


### Main Goals Motivating Interventions on the FX market

- **Price stability**
  - When large exchange rate movements pass-through inflation, generating temporary shocks

- **Financial stability**
        - Calm "disorderly market conditions" (see [link](https://www.imf.org/-/media/Files/Publications/covid19-special-notes/en-special-series-on-covid-19-central-bank-support-for-foreign-exchange-markets.ashx)) for a discussion on how to assess disorderly market conditions)
        - Smooth capital flows and credit spillovers (impact on carry trade and excess returns)
        - Alleviate FX funding shortage
        - Reduce FX speculation

- **Terms of trade**
    - Support external competitiveness (especially during USD weakening phases)
    - Smooth commodity prices fluctuations

- **Building/managing FX reserves**
  - *In principle, without market impact*

- **Support fellow central banks in their exchange rate operations**

BIS Survey (2021) on Central Banks FX Interventions Goals
![BIS Survey Goals](../Slides/fxi_theory_practice/img/bis_fxi_goals.PNG "Title Test")
*Source: BIS 2021 [Link](https://www.bis.org/publ/bppdf/bispap104b_rh.pdf)*

`````{admonition} FXI should be consistent with the central bank's monetary framework
:class: warning
FX interventions should not contradict the central bank mandate, else there is a risk of policy inconsistency (cf. the Mundell Trilemma) that would jeopardize monetary efficiency and central bank credibility
````` 

**Floating exchange rate regimes** (for instance, with inflation targeting) should use FX interventions for:
    * Financial Stability
      * For instance, when domestic agents face severe currency mismatch on their balance sheet, FX volatility is a financial stability threat
  * Preservation of the monetary objectives
    * For instance, when the pass-through of large - and temporary - exchange rate movements threaten the inflation target 
    
**Hard-peg and currency board** regimes typically intervene on the FX market to defend the peg, usually via FX windows, at a fixed exchange rate

**Crawling and soft-peg** conduct infrequent FX interventions when the exchange rate deviates outside of the central bank tolerance
  * However, there is a risk of a conflict between _de-jure_ and _de-facto monetary_ objectives


### FX Intermediate Objectives
The literature (see the BIS below) and international practices typically identify 5 main intermediate objectives:

* **Limit exchange rate volatility**
  * Even if the main goal of the central bank is to maintain price stability, limiting FX volatility is often important. FX volatility affects the price-setting behavior of firms: it causes average imported inflation to rise
  * Excessive FX volatility can also derail the transmission of monetary policy

* **Provide liquidity** to thin market

* **Smooth the path** of the exchange rate

* Limit FX pressure caused by international investors

* Influence the level of the exchange rate (if the main goal of the central bank is indeed an exchange rate nominal anchor)

BIS Survey (2021) on Central Banks FX Interventions Intermediate Objectives
![BIS Survey Objectives](../Slides/fxi_theory_practice/img/bis_intermediate_objectives.PNG "another title test")
*Source: BIS 2021 [Link](https://www.bis.org/publ/bppdf/bispap104b_rh.pdf)*

`````{admonition} FX interventions consistent with floating exchange rate regimes can typically be designed to smooth exchange rate shocks, either:
:class: hint
  * **Permanent shock**: smoothing the exchange rate path dynamic to reach the new equilibrium 
  * **Temporary shock**: smooth the temporary impact while allowing the economy to quickly return back to the previous state
````` 

Example of FX Intervention to Smooth a Permanent Shock
![Permanent shock](../Slides/fxi_theory_practice/img/peru_permanent_shock.PNG)
*Source: IMF and Central Bank of Peru (2018) [Link](https://www.elibrary.imf.org/display/book/9781484375686/ch012.xml)*

Example of FX Intervention to Smooth a Transitory Shock
![Temporary shock](../Slides/fxi_theory_practice/img/peru_transitory_shock.PNG)
*Source: IMF and Central Bank of Peru (2018) [Link](https://www.elibrary.imf.org/display/book/9781484375686/ch012.xml)*


## Risks Associated with FX Interventions

Conducting FX interventions entail risks that central banks should be able to mitigate:

* **Moral hazard** and encouragement of greater risk-taking by market participants
* **Negative effects on market development** :e.g. hampering the development of the derivative markets by removing the need of currency hedge
  * ... which in turn increases the need for future FX interventions by the central bank in the future 
* Potential difficulties in balancing the **orderly functioning of local FX markets while maintaining openness to foreign investors**
* Possible inconsistencies between monetary policy and FX interventions, with complex interactions that are difficult to understand and communicate, which overall increases **policy uncertainty**

_Note that the risk-based FX intervention rule developped by [Lafarguette and Veyrune (2021)](https://www.imf.org/en/Publications/WP/Issues/2021/02/12/Foreign-Exchange-Intervention-Rules-for-Central-Banks-A-Risk-based-Framework-50081) is designed to address some of these issues_


## Sterilization of FX Interventions

### Typology

`````{admonition} Non-Sterilized Interventions
:class: definition
  * Buy and sell foreign assets against banks' reserves at the central bank
  * Increase or decrease the monetary base, and therefore impact the monetary stance
````` 

`````{admonition} Sterilized Interventions
:class: definition
* Buy and sell foreign assets against banks' reserves at the central bank
* Sterilize the intervention by either:
  * selling or purchasing home-currency assets
  * or issuing of sterilization instruments 
* No impact on the monetary stance
````` 

Non-sterilized interventions imply a change of the monetary stance and can directly conflict with the monetary objectives. 

Sterilized interventions should be preferred, as they allow the central bank to isolate their impact to the FX market only. Typically, sterilization is conducted by absorbing liquidity (when buying FX reserves) or by injecting liquidity (when selling FX reserves), so that the volume of banks' reserves at the central bank doesn't change. 

To sterilize, the central bank has to rely on specific operations and instruments:
    - By **buying or selling domestic assets** (usually, domestic sovereign bonds), to offset the impact of the change in foreign reserves (net foreign assets)
    - By **issuing central bank securities** (for instance, sterilization bills or certificates of deposits) to absorb domestic liquidity from banks when buying foreign reserves
    - By **tilting the required reserves ratio (RRR)**, to inject or absorb liquidity. However, it is preferable to keep the RRR stable over time, and this instrument should be use to accomodate structural changes in the liquidity position


Central Bank Analytical Balance Sheet
![CB Balance Sheet](../Slides/fxi_theory_practice/img/central_bank_balance_sheet.PNG)
*Source: Lafarguette*

### Can All Central Banks Sterilize?

In practice, it may be difficult to fully offset the effects of FX interventions as:
  * Countries with under-developed financial markets might not offer enough assets for the central bank to sterilize
  * There are second-round effects that dampen the impact of sterilization
    * _For instance: after FXI (buying), sterilization via domestic assets sale, attracts capital inflows, the CB will have to purchase FX further, etc._

One potential solution is to use **FX derivatives**
  * For instance, some East-Asian central banks have been using FX swaps to sterilize their interventions 
    * Purchasing FX on the spot
    * Swap by selling FX spot, unwinding by buying FX in the future

### The Costs of Sterilization

**Sterilization is often costly** for the central bank, because:
  * **Fiscal costs**
    * Depends on the interest rate differential between domestic and foreign assets, in particular the returns of FX reserves
    * Cost of the conduct of monetary policy with the monetary policy mandate. Important to be consistent, even if it implies costs for the central bank


Central Bank Analytical Balance Sheet with Remuneration and Costs
![CB Balance Sheet](../Slides/fxi_theory_practice/img/central_bank_balance_sheet_rates.PNG)
*Source: Lafarguette*





# Implementation

- Instruments

- Rule vs. Discretion

- FXI Size

- Communication

- Intervention Effectiveness

- FX Interventions and Exchange Rate Management


# Resources

  - A textbook presentation of foreing exchange interventions can be found in Sarno and Taylor (2012): [link](https://www.cambridge.org/core/books/abs/economics-of-exchange-rates/official-intervention-in-the-foreign-exchange-market/539435B26391C092195233098F887850)

 - The IMF has published a guidance note on FX interventions on the spot and derivatives market (2021): [link](https://www.imf.org/-/media/Files/Publications/covid19-special-notes/en-special-series-on-covid-19-central-bank-support-for-foreign-exchange-markets.ashx)           

 - The BIS publishes interesting papers reflecting BIS surveys conducted with central banks. For instance (2019): [link](https://www.bis.org/publ/bppdf/bispap104b-rh.pdf)
    
 - A recent and quite comprehensive database on FX Interventions (2021), compiled by IMF colleagues: [link](https://www.imf.org/en/Publications/WP/Issues/2021/02/19/Foreign-Exchange-Intervention-A-Dataset)

 - Kathryn Dominguez, professor at U-Michigan, specialized on FX interventions: [link](http://www-personal.umich.edu/~kathrynd/index.html)

 - Popper (2022) provides a very complete literature review on FX Interventions: [link](https://www.ssc.wisc.edu/~mchinn/Popper_FXI_apr22.pdf)

- Lafarguette and Veyrune (2021) designed a risk-based framework for FX interventions: [link](https://www.imf.org/en/Publications/WP/Issues/2021/02/12/Foreign-Exchange-Intervention-Rules-for-Central-Banks-A-Risk-based-Framework-50081)

- General useful resource: the IMF Glossary [link](https://www.imf.org/en/About/Glossary)






  
